from abc import ABC, abstractmethod
from browser.provider.generic_browser_provider import GenericBrowserProvider
from tools.csv_handler import CsvHandler


class AbstractScrapper(ABC):
    def __init__(self):
        self.browser = GenericBrowserProvider().get_browser()
        self.storage = CsvHandler('products.csv')

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def execute_main(self):
        pass

    @abstractmethod
    def execute_before(self):
        pass

    @abstractmethod
    def execute_after(self):
        pass

    def get_steps(self, type):
        with open(f'/home/marcelovb/workspace/challenge-ml/src/browser/scrappers/{type}.json', 'r') as file:
            return file.read()

    def save_data(self, data):
        try:
            self.storage.add_product(data)
        except:
            raise Exception("Unable to save products to .csv file.")