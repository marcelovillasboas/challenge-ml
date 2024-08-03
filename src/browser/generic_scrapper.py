import time
import json
import pandas as pd
from datetime import datetime
from browser.scrappers.default_scrapper import AbstractScrapper
from browser.provider.actions.dict import action_dict
from bs4 import BeautifulSoup

class GenericBrowserScrapper(AbstractScrapper):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.steps = json.loads(self.get_steps(self.type))
        if self.steps is None:
            raise Exception("Scraper was not configured.")
        
    def scrape(self, query):
        self.query = query
        self.execute_before()
        product = self.execute_main()
        self.execute_after()
        self.storage.add_product(self, product)
        print("Processing")
        
    def execute_main(self):
        link_path = self.steps["link"]["path"]
        connector = self.steps["link"]["connector"]
        formatted_query = self.query.replace(' ', connector)
        url = link_path + formatted_query
        self.browser.get(url)
        time.sleep(5)
        self.content = self.extraction()
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
        
    def extraction(self):
        self.html = self.browser.page_source

        soup = BeautifulSoup(self.html, "html.parser")

        if self.steps["search"]["custom"]:
            results = soup.find_all(self.steps["search"]["tag"], self.steps["search"]["custom"])
        else:
            results = soup.find_all(self.steps["search"]["tag"], class_=self.steps["search"]["class"])

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
            data.append(product)
        return data
    
    def transform_to_df(self, data):
        df = pd.DataFrame(data)
        df = df.assign(keyword=self.query)
        df = df.assign(source=self.type)
        df = df.assign(execution_date=datetime.now().isoformat())
        df = df.assign(scrapper_type= "Browser")
        return df