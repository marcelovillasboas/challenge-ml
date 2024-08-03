import pandas as pd
from typing import Optional

class Product:
    def __init__(self, product_name: str, price: float, product_url: str,
                 rating: Optional[float] = None, rating_number: Optional[int] = None):
        self.product_name = product_name
        self.price = price
        self.product_url = product_url
        self.rating = rating
        self.rating_number = rating_number

class CsvHandler:
    def __init__(self, filename: str):
        self.filename = filename
        self.headers = ["ProductName", "Price", "ProductUrl", "Rating", "RatingNumber"]
        self._initialize_csv()

    def _initialize_csv(self):
        try:
            df = pd.read_csv(self.filename)
        except FileNotFoundError:
            df = pd.DataFrame(columns=self.headers)
            df.to_csv(self.filename, index=False)

    def add_product(self, product: Product):
        product_data = {
            "ProductName": product.product_name,
            "Price": product.price,
            "ProductUrl": product.product_url,
            "Rating": product.rating,
            "RatingNumber": product.rating_number
        }

        df = pd.read_csv(self.filename)
        df = df.append(product_data, ignore_index=True)
        df.to_csv(self.filename, index=False)
