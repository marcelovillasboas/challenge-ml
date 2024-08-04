from browser.generic_scrapper import GenericSearchScrapper
from browser.superfinanciera_scrapper import SuperFinancieraScrapper

# amazon = GenericSearchScrapper("amazon").scrape("Macbook")
superfinanciera = SuperFinancieraScrapper().scrape()