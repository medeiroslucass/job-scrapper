import platform

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROME_DRIVER_PATH = "/usr/local/bin/chromedriver/chromedriver"
GOOGLE_CHROME_PATH = "/usr/bin/google-chrome"


class CustomWebDriver:

    def get_options(self):
        options = Options()
        options.page_load_strategy = 'eager'

        if not self.is_windows_os():
            print(f"Using Chrome binary at: {GOOGLE_CHROME_PATH}")
            options.binary_location = GOOGLE_CHROME_PATH
            options.add_argument('--headless')

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.137 Safari/537.36')
        return options

    def get_service(self):
        if not self.is_windows_os():
            print(f"Using ChromeDriver at: {CHROME_DRIVER_PATH}")
            service = Service(executable_path=CHROME_DRIVER_PATH)
        else:
            service = Service()

        return service

    def is_windows_os(self):
        return platform.system().lower() == 'windows'
