from abc import ABC, abstractmethod
from browser.provider.generic_browser_provider import GenericBrowserProvider
from tools.csv_handler import CsvHandler


class AbstractScrapper(ABC):
    def __init__(self):
        self.browser_provider = GenericBrowserProvider()
        self.browser = self.browser_provider.get_browser()
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

    def get_steps(self, type): # TODO fix path
        with open(f'/home/marcelovb/workspace/challenge-ml/src/browser/scrappers/{type}.json', 'r') as file:
            return file.read()

    def save_search_data(self, data):
        try:
            self.storage.add_product(data)
        except:
            raise Exception("Unable to save products to .csv file.")
    
    def click(self, by, selector):
        self.browser_provider.click(by, selector)

    def save_pdf_data(self, data):
        try:
            self.storage.save_pdf_info(data)
        except:
            raise Exception("Unable to save pdf info to .csv file.")