import base64
import json
import os
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from selenium.webdriver.common.by import By
from twocaptcha import TwoCaptcha

from browser.scrapers.default_scraper import AbstractScraper

class CaptchaSolver(AbstractScraper):
    def __init__(self, type):
        super().__init__()
        self.type = type
        try:
            self.configs = json.loads(self.get_configs(type))
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception("Failed to load captcha solver configuration.") from e
        
        if not self.configs:
            raise Exception("Captcha solver configuration is empty.")
        
        self.base_dir = os.getcwd()
        self.filename = self.configs["storage"]["filename"]

    def scrape(self):
        try:
            self.execute_before(self.configs)
            time.sleep(int(self.configs["navigation"]["load_timeout"]))
            self.execute_main()
        except Exception as e:
            print(f"An error occurred during scraping: {e}")

    def execute_main(self):
        try:
            self.html = self.browser.page_source
            soup = BeautifulSoup(self.html, "html.parser")
            if self.configs["type"] == 'audio':
                self.get_audio()
                self.transcribe_audio()
            else:
                self.get_image(soup)
                self.solve_captcha()
        except Exception as e:
            raise Exception("Failed to execute main scraping logic.") from e

    def get_image(self, soup: BeautifulSoup):
        try:
            tag = self.configs["script"]["main"]["tag"]
            url_attr = self.configs["script"]["main"]["url"]
            src_prefix = self.configs["script"]["main"]["img"]

            img = soup.find(tag, {url_attr: lambda x: x and x.startswith(src_prefix)})
            if img:
                url = img.get(url_attr)
                if url.startswith(src_prefix):
                    base64_data = url.split(',')[1]
                    image_data = base64.b64decode(base64_data)
                    with open(self.filename, 'wb') as f:
                        f.write(image_data)
                    print(f"Image saved as {self.filename}")
                else:
                    print("Image URL does not match the expected prefix.")
            else:
                print("Image not found in the HTML.")
        except Exception as e:
            raise Exception("Failed to get image.") from e

    def get_audio(self):
        try:
            base_url = self.configs["script"]["main"]["base_url"]
            selector = self.configs["script"]["main"]["selector"]
            audio_id = self.configs["script"]["main"]["audio_id"]

            self.browser_provider.click(selector)
            cookies = {cookie['name']: cookie['value'] for cookie in self.browser.get_cookies()}
            audio_source = self.browser.find_element(By.ID, audio_id)
            audio_url = audio_source.get_attribute('src')
            full_audio_url = urljoin(base_url, audio_url)

            response = requests.get(full_audio_url, cookies=cookies, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP error responses
            with open(self.filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Audio file downloaded as {self.filename}")
        except requests.RequestException as e:
            print(f"Failed to download audio: {e}")
        except Exception as e:
            raise Exception("Failed to get audio.") from e

    def transcribe_audio(self):
        try:
            client = OpenAI()
            with open(os.path.join(self.base_dir, self.filename), 'rb') as audio_file:
                transcription = client.audio.transcriptions.create(
                    model='whisper-1',
                    file=audio_file
                )
            print(transcription.text)
        except FileNotFoundError as e:
            print(f"Audio file not found: {e}")
        except Exception as e:
            raise Exception("Failed to transcribe audio.") from e

    def solve_captcha(self):
        try:
            api_key = os.getenv('SOLVER_API_KEY', '')
            solver = TwoCaptcha(api_key)
            result = solver.normal(os.path.join(self.base_dir, 'captcha_image.png'))
            print(result)
        except Exception as e:
            raise Exception("Failed to solve captcha.") from e
