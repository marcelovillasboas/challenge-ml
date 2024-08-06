import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GenericBrowserProvider:
    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
        self.options = webdriver.ChromeOptions()
        self.default_options = [
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
        
        self._configure_browser()
        self.browser = self._get_browser()

    def _configure_browser(self) -> None:
        """Configure the Chrome browser options and preferences."""
        prefs = {
            "download.default_directory": self.base_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        self.options.add_experimental_option("prefs", prefs)
        for option in self.default_options:
            self.options.add_argument(option)
        self._set_headless_mode()

    def _get_browser(self) -> webdriver.Chrome:
        """Initialize and return a Chrome browser instance."""
        try:
            self.options.binary_location = '/usr/bin/chromium-browser'
            browser = webdriver.Chrome(options=self.options)
            logging.info("Browser initialized successfully.")
            return browser
        except Exception as e:
            logging.error(f"Failed to initialize the browser: {e}")
            raise

    def _set_headless_mode(self) -> None:
        """Set the browser to headless mode based on environment variable."""
        headless = 'True'
        if headless and headless.lower() in ['true', '1']:
            self.options.add_argument("--headless")

    def click(self, selector: str) -> None:
        """Click on an element identified by the XPath selector."""
        try:
            element = self.browser.find_element(By.XPATH, selector)
            element.click()
        except Exception as e:
            logging.error(f"Failed to click on element with selector '{selector}': {e}")
            raise

    def wait_for_download(self, filetype: str, timeout: int = 30) -> bool:
        """Wait for a file of the specified type to be downloaded."""
        elapsed_time = 0
        while elapsed_time < timeout:
            if any(filename.endswith(f'.{filetype}') for filename in os.listdir(self.base_dir)):
                logging.info(f"File of type '{filetype}' has been downloaded.")
                return True
            time.sleep(1)
            elapsed_time += 1
        logging.warning(f"Timeout reached. File of type '{filetype}' not found within {timeout} seconds.")
        return False
