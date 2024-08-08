import pandas as pd
from typing import TypeVar, Generic, List, Union
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

T = TypeVar('T', bound=pd.DataFrame)

class CsvHandler(Generic[T]):
    def __init__(self, filename: str, headers: List[str]):
        self.filename = filename
        self.headers = headers
        self._initialize_csv()

    def _initialize_csv(self) -> None:
        """Initialize the CSV file with headers if it does not exist."""
        try:
            pd.read_csv(f'{self.filename}.csv')
            logging.info(f"CSV file '{self.filename}.csv' already exists.")
        except FileNotFoundError:
            df = pd.DataFrame(columns=self.headers)
            df.to_csv(f'{self.filename}.csv', index=False)
            logging.info(f"CSV file '{self.filename}.csv' created with headers.")

    def save_data(self, data: Union[pd.DataFrame, List[dict]]) -> None:
        """Save the provided data to the CSV file, appending if necessary."""
        try:
            existing_df = pd.read_csv(self.filename)
            if isinstance(data, pd.DataFrame):
                combined_df = pd.concat([existing_df, data], ignore_index=True)
            else:
                new_data_df = pd.DataFrame(data, columns=self.headers)
                combined_df = pd.concat([existing_df, new_data_df], ignore_index=True)
        except FileNotFoundError:
            if isinstance(data, pd.DataFrame):
                combined_df = data
            else:
                combined_df = pd.DataFrame(data, columns=self.headers)
        
        try:
            combined_df.to_csv(f'{self.filename}.csv', index=False)
        except Exception as e:
            logging.error(f"Failed to save data to '{self.filename}.csv': {e}")
            raise
