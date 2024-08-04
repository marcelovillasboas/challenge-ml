import json
import os
from browser.scrappers.default_scrapper import AbstractScrapper
from browser.provider.actions.dict import action_dict
from bs4 import BeautifulSoup
import pdfplumber
import pytesseract

class SuperFinancieraScrapper(AbstractScrapper):
    def __init__(self):
        super().__init__()
        self.steps = json.loads(self.get_steps('superfinanciera'))
        if self.steps is None:
            raise Exception("Scrapper was not configured.")
        
    def scrape(self):
        self.execute_before()
        self.execute_main()
        self.execute_after()
        print("Data saved to file.")

    def execute_before(self):
        before = self.steps["script"]["before"]
        if before:
            for action in before:
                if action_dict[action] is None:
                    raise Exception("Script was not defined.")
                action_dict[action](self.browser, before[action])
            return
        
    def execute_main(self):
        self.html = self.browser.page_source
        soup = BeautifulSoup(self.html, "html.parser")

        table = soup.find(self.steps["table"]["tag"], class_=self.steps["table"]["class"])
        tbody = table.find_all(self.steps["table"]["table_body"])[1]
        first_row = tbody.find_all(self.steps["table"]["table_row"])[0]

        columns = first_row.find_all(self.steps["table"]["table_column"])
        row_data = [column.get_text(strip=True) for column in columns]

        print(f'Extracted data => {row_data}')

        self.browser_provider.click(self.steps["table"]["first_element"])
        self.browser_provider.wait_for_download()
        
        self.browser.quit()
        return self
        
    def execute_after(self):
        download_dir = "/home/marcelovb/workspace/challenge-ml/" # TODO fix path
        for filename in os.listdir(download_dir): 
            if filename.endswith('.pdf'):
                file_path = os.path.join(download_dir, filename)
                pdf_text = self.extract_text_from_pdf(file_path)
                print(f'Extracted text (from pdf) => {pdf_text}')

    def extract_text_from_pdf(self, dir):
        text = ""
        with pdfplumber.open(dir) as pdf:
            for page in pdf.pages:
                im = page.to_image()
                img = im.original
                text += pytesseract.image_to_string(img)
        return text                
