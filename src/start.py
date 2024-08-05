from browser.generic_scraper import GenericBrowserSearchScraper
from browser.superfinanciera_scraper import SuperFinancieraScraper
from browser.captcha import CaptchaSolver
from request.generic_scraper import GenericRequestSearchScraper

# superfinanciera = SuperFinancieraScraper().scrape()
# amazon = GenericBrowserSearchScraper("amazon").scrape("macbook")
captcha = CaptchaSolver('trf4').scrape()