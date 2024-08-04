import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class GenericBrowserProvider:
    browser: None
    options = webdriver.ChromeOptions()

    default_options = [
        "--remote-debugging-port=9222",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-setuid-sandbox",
        "--disable-web-security",
        "--disable-dev-shm-usage",
        "--memory-pressure-off",
        "--ignore-certificate-errors",
        "--disable-features=site-per-process",
        "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    ]

    def __init__(self):
        prefs = {
            "download.default_directory": "/home/marcelovb/workspace/challenge-ml/", # TODO fix path
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        self.options.add_experimental_option("prefs", prefs)
        for option in self.default_options:
            self.options.add_argument(option)
        self.is_headless()
        self.browser = self.get_browser()

    def get_browser(self):
        self.options.binary_location = '/usr/bin/chromium-browser'
        return webdriver.Chrome(options=self.options)
    
    def is_headless(self):
        headless = os.getenv('HEADLESS')
        if headless is None:
            self.options.add_argument("--headless")

    def click(self, selector):
        element = self.browser.find_element(By.XPATH, selector)
        element.click()

    def wait_for_download(self, timeout=30):
        seconds = 0
        while not any([filename.endswith('.pdf') for filename in os.listdir("/home/marcelovb/workspace/challenge-ml/")]):
            time.sleep(1)
            seconds += 1
            if seconds > timeout:
                break

    # def set_proxy(self):
    #     if os.getenv("USE_PROXY"):
    #         user  = os.getenv("PROXY_USER")
    #         password = os.getenv("PROXY_PASSWORD")
    #         url = os.getenv("PROXY_URL")
    #         port = os.getenv("PROXY_PORT")
    #         proxy_provider = f'http://{user}:{password}@{url}:{port}'
    #         self.options.add_argument(f'--proxy-server={proxy_provider}')

    # def set_options(self, args: list[str] | None):
    #     self.is_headless()
    #     # self.set_proxy()
    #     if args:
    #         for arg in args:
    #             self.options.add_argument(arg)
    
    
