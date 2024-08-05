import base64
import json
import time
from openai import OpenAI
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
from browser.scrapers.default_scraper import AbstractScraper
from browser.provider.actions.dict import action_dict
from twocaptcha import TwoCaptcha
from selenium.webdriver.common.by import By

class CaptchaSolver(AbstractScraper):
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.configs = json.loads(self.get_configs(type))
        if self.configs is None:
            raise Exception("Captcha solver was not configured.")
    
    def scrape(self): 
        self.execute_before(self.configs)
        self.execute_main()
        self.solve_captcha()

    def execute_main(self):
        self.html = self.browser.page_source
        soup = BeautifulSoup(self.html, "html.parser")
        type = self.configs["type"]
        if type == 'audio':
            self.get_audio(soup)
            self.transcribe_audio()
        else:
            self.get_image(soup)
    
    def get_image(self, soup: BeautifulSoup):
        tag = self.configs["script"]["main"]["tag"]
        url = self.configs["script"]["main"]["url"]
        src = self.configs["script"]["main"]["img"]
        filename = self.configs["storage"]["filename"]
        img = soup.find(tag, { url: lambda x: x and x.startswith(src) })
        if img:
            url = img.get(url)
            if url.startswith(src):
                base64_data = url.split(',')[1]
                image_data = base64.b64decode(base64_data)
                with open(filename, 'wb') as f:
                    f.write(image_data)
    
    def get_audio(self, soup: BeautifulSoup):
        base_url = 'https://sei.trf4.jus.br/'
        self.browser_provider.click('//*[@id="infraImgAudioCaptcha"]')
        cookies = self.browser.get_cookies()
        cookies_dict = { cookie['name']: cookie['value'] for cookie in cookies }
        audio_source = self.browser.find_element(By.ID, 'infraSrcAudioCaptcha')
        audio_url = audio_source.get_attribute('src')
        full_audio_url = urljoin(base_url, audio_url)

        response = requests.get(full_audio_url, cookies=cookies_dict, stream=True)
        if response.status_code == 200:
            with open('captcha.wav', 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Audio file downloaded as captcha.wav")
        else:
            print(f"Failed to download audio: {response.status_code}")
    
    def transcribe_audio(self):
        client = OpenAI()
        audio_file = open('/home/marcelovb/workspace/challenge-ml/captcha.wav', 'rb') ## TODO fix path
        transcription = client.audio.transcriptions.create(
            model='whisper-1',
            file=audio_file
        )
        print(transcription.text)

        
    def solve_captcha(self):
        solver = TwoCaptcha('79d921b0bae570b9bf9d9eee3b31fd76') # TODO remove
        result = solver.normal('/home/marcelovb/workspace/challenge-ml/captcha_image.png') # TODO fix path
        print(result)
        
