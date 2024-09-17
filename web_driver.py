import logging
import platform

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

if platform.system().lower() == 'windows':
    GOOGLE_CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"
elif platform.system().lower() == 'darwin':  # macOS
    GOOGLE_CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else:
    GOOGLE_CHROME_PATH = "/usr/bin/google-chrome"


class CustomWebDriver:
    def get_options(self):
        options = Options()
        options.page_load_strategy = 'eager'

        logging.info(f"Using Chrome binary at: {GOOGLE_CHROME_PATH}")
        if platform.system().lower() != 'windows':
            options.binary_location = GOOGLE_CHROME_PATH
            options.add_argument('--headless')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.137 Safari/537.36')
        return options

    def get_service(self):
        # Return the Service object created with ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        return service
