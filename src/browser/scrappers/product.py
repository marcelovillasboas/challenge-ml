from typing import Optional

class Product:
    def __init__(self, product_name: str, price: float, product_url: str,
                 rating: Optional[float] = None, rating_number: Optional[int] = None):
        self.product_name = product_name
        self.price = price
        self.product_url = product_url
        self.rating = rating
        self.rating_number = rating_number
