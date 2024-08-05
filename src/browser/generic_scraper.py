import time
import json
import pandas as pd
from datetime import datetime
from browser.scrapers.default_scraper import AbstractScraper
from browser.provider.actions.dict import action_dict
from bs4 import BeautifulSoup

class PageLoadException(Exception):
    pass

class GenericBrowserSearchScraper(AbstractScraper):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.page_counter = 1
        self.content = []
        self.configs = json.loads(self.get_configs(self.type))
        if self.configs is None:
            raise Exception("Scrapper was not configured.")
        
    def scrape(self, query):
        self.query = query
        self.execute_before(self.configs)
        self.execute_main()
        self.execute_after(self.configs)
        self.analyze_df(self.content)
        self.save_data(self.content, self.configs["storage"]["filename"], self.configs["storage"]["headers"])
        print("Data saved to file.")
        
    def execute_main(self):
        pages_to_scrape = int(self.configs["navigation"]["pages"])
        load_timeout = int(self.configs["navigation"]["load_timeout"])
        while self.page_counter <= pages_to_scrape:
            try: 
                url = self.get_url(self.page_counter)
                self.browser.get(url)
                time.sleep(load_timeout)
                extraction = self.extract()
                for result in extraction:
                    self.content.append(result)
                self.page_counter = self.page_counter + 1
            except PageLoadException:
                print(f'Failed to load page. Retrying... Page number => {self.page_counter} | Keyword => {self.query}')
                continue
        
        self.content = self.transform_to_df(self.content)
        self.browser.quit()
        return self
        
    def extract(self):
        self.html = self.browser.page_source
        soup = BeautifulSoup(self.html, "html.parser")
        results = self.extract_page(soup)

        data = []
        for result in results:
            product = {}
            primary_success = True

            for step in self.configs['product']:
                value = self.configs['product'][step]
                try:
                    content = eval(value)
                    product[step] = content
                except:
                    if step == 'name':
                        primary_success = False
                        break
                    product[step] = None

            if not primary_success:
                product_alt = {}
                for alt_step in self.configs['product_alt']:
                    alt_value = self.configs['product_alt'][alt_step]
                    try:
                        content = eval(alt_value)
                        product_alt[alt_step] = content
                    except:
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
        main_container = soup.find(self.configs["search"]["tag"], class_=self.configs["search"]["main_container"])
        if not main_container:
            raise PageLoadException("Main container not found.")
        
        results = main_container.find_all(self.configs["search"]["tag"], attrs=self.configs["search"]["attribute"])
        return results

    def get_url(self, page = 1):
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
    
    def transform_to_df(self, data):
        df = pd.DataFrame(data)
        df = df.assign(keyword=self.query)
        df = df.assign(source=self.type)
        df = df.assign(execution_date=datetime.now().isoformat())
        df = df.assign(scrapper_type="Browser")
        return df

    def analyze_df(self, df: pd.DataFrame):
        total_products = df['name'].nunique()
        top_expensive = df.sort_values(by='price', ascending=False).head(10)
        products_per_page = df['page'].value_counts()
        print("Total number of products:", total_products)
        print("Top 10 Most Expensive Products:\n", top_expensive)
        print("Products per Page:\n", products_per_page)
        return
