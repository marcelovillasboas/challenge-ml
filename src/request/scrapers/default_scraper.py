from abc import ABC, abstractmethod

from tools.csv_handler import CsvHandler

class AbstractScraper(ABC):
    @abstractmethod
    def scrape(self):
        pass

    def get_configs(self, type): # TODO fix path
        with open(f'/home/marcelovb/workspace/challenge-ml/src/request/scrapers/{type}.json', 'r') as file:
            return file.read()
        
    def save_data(self, data, filename, headers):
        self.storage = CsvHandler(filename, headers)
        try:
            self.storage.save_data(data)
        except:
            raise Exception("Unable to save data to .csv file.")
