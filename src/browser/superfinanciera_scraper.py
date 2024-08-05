from datetime import datetime
import json
import os

import pandas as pd
from browser.scrapers.default_scraper import AbstractScraper
from browser.provider.actions.dict import action_dict
from bs4 import BeautifulSoup
import pdfplumber
import pytesseract

class SuperFinancieraScraper(AbstractScraper):
    def __init__(self):
        super().__init__()
        self.configs = json.loads(self.get_configs('superfinanciera'))
        if self.configs is None:
            raise Exception("Scraper was not configured.")
        
    def scrape(self):
        self.execute_before(self.configs)
        self.execute_main()
        self.execute_after()
        self.save_data(self.content, self.configs["storage"]["filename"], self.configs["storage"]["headers"])
        print("Data saved to file.")

    # def execute_before(self):
    #     before = self.configs["script"]["before"]
    #     if before:
    #         for action in before:
    #             if action_dict[action] is None:
    #                 raise Exception("Script was not defined.")
    #             action_dict[action](self.browser, before[action])
    #         return
        
    def execute_main(self):
        self.html = self.browser.page_source
        soup = BeautifulSoup(self.html, "html.parser")

        table = soup.find(self.configs["table"]["tag"], class_=self.configs["table"]["class"])
        tbody = table.find_all(self.configs["table"]["table_body"])[1]
        first_row = tbody.find_all(self.configs["table"]["table_row"])[0]

        columns = first_row.find_all(self.configs["table"]["table_column"])
        self.row_data = [column.get_text(strip=True) for column in columns]

        self.browser_provider.click(self.configs["table"]["first_element"])
        self.browser_provider.wait_for_download('pdf')
        
        self.browser.quit()
        return self
        
    def execute_after(self):
        download_dir = "/home/marcelovb/workspace/challenge-ml/" # TODO fix path
        for filename in os.listdir(download_dir): 
            if filename.endswith('.pdf'):
                file_path = os.path.join(download_dir, filename)
                self.pdf_text = self.extract_text_from_pdf(file_path)
                self.content = self.transform_to_df()

    def extract_text_from_pdf(self, dir):
        text = ""
        with pdfplumber.open(dir) as pdf:
            for page in pdf.pages:
                im = page.to_image()
                img = im.original
                text += pytesseract.image_to_string(img)
        return text
    
    def transform_to_df(self):
        columns = self.configs["consolidation"]["columns"]
        data = self.row_data + [self.pdf_text]
        df = pd.DataFrame([data], columns=columns)
        df = df.assign(execution_date=datetime.now().isoformat())
        return df
