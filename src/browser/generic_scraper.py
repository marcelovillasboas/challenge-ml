import os
import time
import json
import logging
import pandas as pd
from datetime import datetime
from browser.scrapers.default_scraper import AbstractScraper
from browser.provider.actions.dict import action_dict
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PageLoadException(Exception):
    pass

class GenericBrowserSearchScraper(AbstractScraper):
    def __init__(self, type: str):
        super().__init__()
        self.type = type
        self.page_counter = 1
        self.content = []
        self.configs = json.loads(self.get_configs(self.type))
        if self.configs is None:
            logging.error("Scraper configuration is missing.")
            raise Exception("Scraper was not configured.")
        
    def scrape(self, query: str):
        self.query = query
        try:
            self.execute_before(self.configs)
            self.execute_main()
            self.execute_after(self.configs)
            self.analyze_df(self.content)
            self.save_data(self.content, self.configs["storage"]["filename"], self.configs["storage"]["headers"])
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
        
    def execute_main(self):
        pages_to_scrape = int(self.configs["navigation"]["pages"])
        load_timeout = int(self.configs["navigation"]["load_timeout"])
        while self.page_counter <= pages_to_scrape:
            try: 
                url = self.get_url(self.page_counter)
                self.browser.get(url)
                time.sleep(load_timeout)
                extraction = self.extract()
                self.content.extend(extraction)
                self.page_counter += 1
            except (PageLoadException, TimeoutException, NoSuchElementException) as e:
                logging.warning(f'Failed to load page {self.page_counter} for keyword "{self.query}": {e}. Retrying...')
                continue
            except Exception as e:
                logging.error(f"Unexpected error on page {self.page_counter}: {e}")
                break
        
        self.content = self.transform_to_df(self.content)
        self.browser.quit()
        
    def extract(self):
        self.html = self.browser.page_source
        soup = BeautifulSoup(self.html, "html.parser")
        results = self.extract_page(soup)

        data = []
        for result in results:
            product = {}
            primary_success = True

            for step, value in self.configs['product'].items():
                try:
                    content = eval(value)
                    product[step] = content
                except Exception as e:
                    if step == 'name':
                        primary_success = False
                        break
                    product[step] = None

            if not primary_success:
                product_alt = {}
                for alt_step, alt_value in self.configs['product_alt'].items():
                    try:
                        content = eval(alt_value)
                        product_alt[alt_step] = content
                    except Exception as e:
                        product_alt[alt_step] = None

                if product_alt.get('name'):
                    data.append({**product_alt, 'page': self.page_counter})
                    continue

            if product.get('rating') == 'N/A':
                product['rating_number'] = 'N/A'

            data.append({**product, 'page': self.page_counter})

        if len(data) > 4:
            data = data[1:]
            data = data[:-4]

        return data
    
    def extract_page(self, soup: BeautifulSoup):
        try:
            main_container = soup.find(self.configs["search"]["tag"], class_=self.configs["search"]["main_container"])
            if not main_container:
                raise PageLoadException("Main container not found")
            
            results = main_container.find_all(self.configs["search"]["tag"], attrs=self.configs["search"]["attribute"])
            return results
        except Exception as e:
            raise PageLoadException(e)

    def get_url(self, page: int = 1) -> str:
        link_path = self.configs["link"]["path"]
        keyword_connector = self.configs["link"]["connector"]
        query_connector = self.configs["link"]["query_connector"]
        page_prefix = self.configs["link"]["page_prefix"]
        formatted_query = self.query.replace(' ', keyword_connector)
        if page != 1:
            url = link_path + formatted_query + query_connector + page_prefix + str(page)
        else:
            url = link_path + formatted_query
        return url
    
    def transform_to_df(self, data: list) -> pd.DataFrame:
        try:
            df = pd.DataFrame(data)
            df = df.assign(keyword=self.query)
            df = df.assign(source=self.type)
            df = df.assign(execution_date=datetime.now().isoformat())
            df = df.assign(scraper_type="Browser")
            return df
        except Exception as e:
            logging.error(f"Failed to transform data to DataFrame: {e}")
            raise

    def analyze_df(self, df: pd.DataFrame):
        try:
            total_products = df['name'].nunique()
            products_per_page = df['page'].value_counts()

            insights = pd.DataFrame({
                'Total Unique Products': [total_products],
                'Products per Page': [products_per_page.to_dict()]
            })

            logging.info(f"Total number of products: {total_products}")
            logging.info(f"Products per Page:\n{products_per_page}")
            self.save_data(insights, 'insights', ['Total Unique Products', 'Products per Page'])
        except Exception as e:
            logging.error(f"Failed to analyze DataFrame: {e}")
