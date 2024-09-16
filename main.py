import json
import logging
from datetime import datetime

from bs4 import BeautifulSoup
from pytz import timezone
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from record import JobRecord
from web_driver import CustomWebDriver

DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

with open('config.json') as config_file:
    config = json.load(config_file)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Bot:
    def __init__(self, url: str) -> None:
        self.driver = CustomWebDriver()
        self.browser = webdriver.Chrome(
            service=self.driver.get_service(), options=self.driver.get_options())
        self.url = url

    def close_cookies_banner(self) -> None:
        try:
            cookies_button = WebDriverWait(self.browser, 5).until(
                EC.element_to_be_clickable(
                    (By.ID, "onetrust-accept-btn-handler"))
            )
            cookies_button.click()
            logging.info("Closed cookie banner.")
        except (NoSuchElementException, TimeoutException):
            logging.info("Cookie banner not found or already closed.")

    def wait_for_elements(self, by: By, value: str, timeout: int = 10) -> None:
        try:
            WebDriverWait(self.browser, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logging.error("Elements were not loaded in time.")
            raise

    def click_next_page(self) -> bool:
        try:
            next_button = WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, config['next_page_selector']))
            )

            if next_button.is_enabled():
                WebDriverWait(self.browser, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, config['next_page_selector']))
                )
                next_button.click()
                return True
            else:
                logging.info(
                    "'Next' button found, but disabled. Ending the collection.")
                return False

        except (NoSuchElementException, TimeoutException):
            logging.info("No more pages to scroll through.")
            return False

        except Exception as e:
            logging.error(f"Error trying to advance to the next page: {e}")
            return False

    def get_scrape_data(self) -> None:
        self.browser.get(self.url)
        all_records = []

        self.close_cookies_banner()

        while True:
            try:
                self.wait_for_elements(By.CLASS_NAME, 'job_seen_beacon')
            except TimeoutException:
                break

            page_source = self.browser.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            cards = soup.select(config['job_card_selector'])
            logging.info(f'Number of cards found on the page: {len(cards)}')

            records = self.get_jobs(cards)
            all_records.extend(records)

            if not self.click_next_page():
                break

        logging.info(f"Total records obtained: {len(all_records)}")
        data = [record.__dict__ for record in all_records]

        with open('jobs.json', 'w', newline='') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def get_brasilia_date_time_str(self) -> str:
        return datetime.now(timezone('America/Sao_Paulo')).strftime(DATE_TIME_FORMAT)

    def convert_to_record(self, card) -> JobRecord:
        record = JobRecord()
        url_template = "https://br.indeed.com/viewjob?jk={}"

        element = card.find('a')
        record.job_source_id = element['data-jk']
        record.job_title = element.get_text(strip=True)
        record.job_url = url_template.format(record.job_source_id)

        company_element = card.select_one('span[data-testid="company-name"]')
        record.company = company_element.get_text(
            strip=True) if company_element else ''

        location_element = card.select_one('div[data-testid="text-location"]')
        record.location = location_element.get_text(
            strip=True) if location_element else ''

        record.job_date = self.get_brasilia_date_time_str()

        return record

    def get_jobs(self, cards: list) -> list:
        return [self.convert_to_record(card) for card in cards if card]

    def close_browser(self) -> None:
        self.browser.quit()


if __name__ == '__main__':
    url = config['url_base']
    bot = Bot(url)
    try:
        bot.get_scrape_data()
    finally:
        bot.close_browser()
