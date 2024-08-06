from browser.generic_scraper import GenericBrowserSearchScraper
from browser.superfinanciera_scraper import SuperFinancieraScraper
from browser.captcha import CaptchaSolver

amazon = GenericBrowserSearchScraper("amazon").scrape("macbook")
superfinanciera = SuperFinancieraScraper().scrape()
captcha_audio = CaptchaSolver('trf4').scrape()
captcha_img = CaptchaSolver('tjsc').scrape()
