import json
import os
from datetime import datetime
import time

import pandas as pd
from bs4 import BeautifulSoup
import pdfplumber
import pytesseract

from browser.scrapers.default_scraper import AbstractScraper

class SuperFinancieraScraper(AbstractScraper):
    def __init__(self):
        super().__init__()
        try:
            self.configs = json.loads(self.get_configs('superfinanciera'))
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception("Failed to load scraper configuration.") from e
        
        if not self.configs:
            raise Exception("Scraper configuration is empty.")
        
        self.content = []

    def scrape(self):
        try:
            self.execute_before(self.configs)
            time.sleep(int(self.configs["navigation"]["load_timeout"]))
            self.execute_main()
            self.execute_after()
            self.save_data(self.content, self.configs["storage"]["filename"], self.configs["storage"]["headers"])
            print("Data saved to file.")
        except Exception as e:
            print(f"An error occurred during scraping: {e}")

    def execute_main(self):
        try:
            self.html = self.browser.page_source
            soup = BeautifulSoup(self.html, "html.parser")

            table = soup.find(self.configs["table"]["tag"], class_=self.configs["table"]["class"])
            if not table:
                raise ValueError("Table not found on the page.")
            
            tbody = table.find_all(self.configs["table"]["table_body"])[1]
            first_row = tbody.find_all(self.configs["table"]["table_row"])[0]

            columns = first_row.find_all(self.configs["table"]["table_column"])
            self.row_data = [column.get_text(strip=True) for column in columns]

            self.browser_provider.click(self.configs["table"]["first_element"])
            self.browser_provider.wait_for_download('pdf')
        except Exception as e:
            raise Exception("Failed to execute main scraping logic.") from e
        finally:
            self.browser.quit()

    def execute_after(self):
        try:
            download_dir = self.base_dir
            pdf_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
            if not pdf_files:
                raise FileNotFoundError("No PDF files found in the download directory.")
            
            file_path = os.path.join(download_dir, pdf_files[0])
            self.pdf_text = self.extract_text_from_pdf(file_path)
            self.content = self.transform_to_df()
        except Exception as e:
            raise Exception("Failed to execute post-scraping logic.") from e

    def extract_text_from_pdf(self, file_path):
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += pytesseract.image_to_string(page.to_image().original)
        except Exception as e:
            raise Exception("Failed to extract text from PDF.") from e
        return text

    def transform_to_df(self):
        try:
            columns = self.configs["consolidation"]["columns"]
            data = self.row_data + [self.pdf_text]
            df = pd.DataFrame([data], columns=columns)
            df = df.assign(execution_date=datetime.now().isoformat())
        except Exception as e:
            raise Exception("Failed to transform data into DataFrame.") from e
        return df
