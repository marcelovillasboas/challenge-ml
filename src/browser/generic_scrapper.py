import time
import json
import pandas as pd
from datetime import datetime
from browser.scrappers.default_scrapper import AbstractScrapper
from browser.provider.actions.dict import action_dict
from bs4 import BeautifulSoup

class PageLoadException(Exception):
    pass

class GenericSearchScrapper(AbstractScrapper):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.page_counter = 1
        self.content = []
        self.steps = json.loads(self.get_steps(self.type))
        if self.steps is None:
            raise Exception("Scrapper was not configured.")
        
    def scrape(self, query):
        self.query = query
        self.execute_before()
        self.execute_main()
        self.execute_after()
        self.save_search_data(self.content)
        print("Data saved to file.")
        
    def execute_main(self):
        pages_to_scrape = int(self.steps["navigation"]["pages"])
        load_timeout = int(self.steps["navigation"]["load_timeout"])
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
        
        
    def execute_before(self):
        before = self.steps["script"]["before"]
        if before:
            for action in before:
                if action_dict[action] is None:
                    raise Exception("Script was not defined.")
                action_dict[action](self.browser, before[action])
            return
        
    def execute_after(self):
        after = self.steps["script"]["after"]
        if after:
            for action in after:
                if action_dict[action] is None:
                    raise Exception("Script was not defined")
                action_dict[action](self.browser, after[action])
            return
    
    def get_url(self, page = 1):
        link_path = self.steps["link"]["path"]
        keyword_connector = self.steps["link"]["connector"]
        query_connector = self.steps["link"]["query_connector"]
        page_prefix = self.steps["link"]["page_prefix"]
        formatted_query = self.query.replace(' ', keyword_connector)
        if page != 1:
            url = link_path + formatted_query + query_connector + page_prefix + str(page)
        else:
            url = link_path + formatted_query
        return url

        
    def extract(self):
        self.html = self.browser.page_source

        soup = BeautifulSoup(self.html, "html.parser")
        
        results = self.extract_page(soup)

        data = []
        for result in results:
            product = {}
            for step in self.steps["product"]:
                value = self.steps["product"][step]
                try:
                    content = eval(value)
                except:
                    content = None
                product[step] = content

            if product.get('rating') == 'N/A':
                product['rating_number'] = 'N/A'
            data.append({ **product, 'page': self.page_counter })
        return data
    
    def extract_page(self, soup: BeautifulSoup):
        main_container = soup.find(self.steps["search"]["tag"], class_=self.steps["search"]["main_container"])

        if not main_container:
            raise PageLoadException("Main container not found.")

        results = main_container.find_all(self.steps["search"]["tag"], attrs=self.steps["search"]["attribute"])
        
        return results

    
    def transform_to_df(self, data):
        df = pd.DataFrame(data)
        df = df.assign(keyword=self.query)
        df = df.assign(source=self.type)
        df = df.assign(execution_date=datetime.now().isoformat())
        df = df.assign(scrapper_type= "Browser")
        return df
