from abc import ABC, abstractmethod
from browser.provider.generic_browser_provider import GenericBrowserProvider
from tools.csv_handler import CsvHandler
from browser.provider.actions.dict import action_dict


class AbstractScraper(ABC):
    def __init__(self):
        self.browser_provider = GenericBrowserProvider()
        self.browser = self.browser_provider.get_browser()

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def execute_main(self):
        pass

    
    def execute_before(self, configs):
        before = configs["script"]["before"]
        if before:
            for action in before:
                if action_dict[action] is None:
                    raise Exception("Script was not defined.")
                action_dict[action](self.browser, before[action])
            return

    def execute_after(self, configs):
        after = configs["script"]["after"]
        if after:
            for action in after:
                if action_dict[action] is None:
                    raise Exception("Script was not defined")
                action_dict[action](self.browser, after[action])
            return

    def get_configs(self, type): # TODO fix path
        with open(f'/home/marcelovb/workspace/challenge-ml/src/browser/scrapers/configs/{type}.json', 'r') as file:
            return file.read()

    def save_data(self, data, filename, headers):
        self.storage = CsvHandler(filename, headers)
        try:
            self.storage.save_data(data)
        except:
            raise Exception("Unable to save data to .csv file.")

