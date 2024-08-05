from request.scrapers.default_scraper import AbstractScraper
import json
import requests
import random
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup

class PageLoadException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    pass

class GenericRequestSearchScraper(AbstractScraper):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.page_counter = 1
        self.content = []
        self.configs = json.loads(self.get_configs(self.type))
        if self.configs is None:
            raise Exception("Scraper was not configured.")

    def scrape(self, query):
        self.query = query
        self.get_data()
        self.save_data(self.content, self.configs["storage"]["filename"], self.configs["storage"]["headers"])
        print("Data saved to file.")

    def get_data(self):
        session  = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]

        pages_to_scrape = int(self.configs["navigation"]["pages"])

        while self.page_counter <= pages_to_scrape:
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive"
            }
            try:
                url = self.get_url(self.page_counter)
                response = session.get(url, headers=headers)
                response.raise_for_status()
                if response.status_code > 400:
                    raise PageLoadException(f'Request failed. Status code {response.status_code}')
                self.data = response.text
                extraction = self.extract()
                for result in extraction:
                    self.content.append(result)
                self.page_counter = self.page_counter + 1
            except PageLoadException as e:
                print(f'Request failed. Retrying... Page number => {self.page_counter} | Keyword => {self.query} | Error => {e.message}')
                continue

    def extract(self):
        soup = BeautifulSoup(self.data, 'html.parser')

        results = self.extract_page(soup)

        data = []
        for result in results:
            product = {}
            for step in self.configs["product"]:
                value = self.configs["product"][step]
                try:
                    content = eval(value)
                except:
                    content = None
                product[step] = content

            if product.get('rating') == 'N/A':
                product['rating_number'] = 'N/A'
            data.append({ **product, 'page': self.page_counter })
        return data

    def extract_page(self, soup: BeautifulSoup):
        main_container = soup.find(self.configs["search"]["tag"], class_=self.configs["search"]["main_container"])
        if not main_container:
            raise PageLoadException("Main container not found.")
        
        results = main_container.find_all(self.configs["search"]["tag"], attrs=self.configs["search"]["attribute"])
        return results
    
    def get_url(self, page = 1):
        link_path = self.configs["link"]["path"]
        keyword_connector = self.configs["link"]["connector"]
        query_connector = self.configs["link"]["query_connector"]
        page_prefix = self.configs["link"]["page_prefix"]
        formatted_query = self.query.replace(' ', keyword_connector)
        if page != 1:
            url = link_path + formatted_query + query_connector + page_prefix + str(page)
        else:
            url = link_path + formatted_query
        return url
