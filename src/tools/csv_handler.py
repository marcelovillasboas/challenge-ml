import pandas as pd
from browser.scrappers.product import Product

class CsvHandler:
    def __init__(self, filename: str):
        self.filename = filename
        self.headers = ["name", "price", "url", "rating", "rating_number", "page"]
        self._initialize_csv()

    def _initialize_csv(self):
        try:
            df = pd.read_csv(self.filename)
        except FileNotFoundError:
            df = pd.DataFrame(columns=self.headers)
            df.to_csv(self.filename, index=False)

    def add_product(self, product: Product):
        try:
            existing_df = pd.read_csv(self.filename)
            combined_df = pd.concat([existing_df, product], ignore_index=True)
        except FileNotFoundError:
            combined_df = product

        combined_df.to_csv(self.filename, index=False)

        
