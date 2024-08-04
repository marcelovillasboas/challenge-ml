from typing import Optional

class Product:
    def __init__(self, name: str, price: float, url: str, page: int,
                 rating: Optional[float] = None, rating_number: Optional[int] = None):
        self.name = name
        self.price = price
        self.url = url
        self.rating = rating
        self.rating_number = rating_number
        self.page = page
