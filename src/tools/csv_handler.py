import pandas as pd
from typing import TypeVar, Generic

T = TypeVar('T')
class CsvHandler(Generic[T]):
    def __init__(self, filename: str, headers):
        self.filename = filename
        self.headers = headers
        self._initialize_csv()

    def _initialize_csv(self):
        try:
            df = pd.read_csv(f'{self.filename}.csv')
        except FileNotFoundError:
            df = pd.DataFrame(columns=self.headers)
            df.to_csv(f'{self.filename}.csv', index=False)
    
    def save_data(self, data: T):
        try:
            existing_df = pd.read_csv(self.filename)
            combined_df = pd.concat([existing_df, data], ignore_index=True)
        except FileNotFoundError:
            combined_df = data
        
        combined_df.to_csv(f'{self.filename}.csv', index=False)

# class CsvHandler:
#     def __init__(self, filename: str):
#         self.filename = filename
#         self.headers = ["name", "price", "url", "rating", "rating_number", "page"]
#         self._initialize_csv()

#     def _initialize_csv(self):
#         try:
#             df = pd.read_csv(self.filename)
#         except FileNotFoundError:
#             df = pd.DataFrame(columns=self.headers)
#             df.to_csv(self.filename, index=False)

#     def add_product(self, product: Product):
#         try:
#             existing_df = pd.read_csv(self.filename)
#             combined_df = pd.concat([existing_df, product], ignore_index=True)
#         except FileNotFoundError:
#             combined_df = product

#         combined_df.to_csv(self.filename, index=False)

#     def save_pdf_info(self, pdf_info): # TODO fix
#         try:
#             pdf_info.to_csv()
#         except:
#             raise Exception('Failed to save pdf info into .csv file.')
        
