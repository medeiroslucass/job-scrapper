import csv
import json
from datetime import datetime

from pytz import timezone
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from record import JobRecord
from web_driver import CustomWebDriver

DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Bot():

    def __init__(self, url) -> None:
        self.driver = CustomWebDriver()
        self.url = url

    def close_cookies_banner(self, browser):
        try:
            cookies_button = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable(
                    (By.ID, "onetrust-accept-btn-handler"))
            )
            cookies_button.click()
            print("Closed cookie banner.")
        except (NoSuchElementException, TimeoutException):
            print("Cookie banner not found or already closed.")

    def get_scrape_data(self):
        cards = []

        browser = webdriver.Chrome(
            service=self.driver.get_service(), options=self.driver.get_options())
        browser.get(self.url)

        all_records = []

        self.close_cookies_banner(browser)

        while True:
            try:
                WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, 'job_seen_beacon'))
                )
            except TimeoutException:
                print("Elements were not loaded in time.")
                break

            cards = browser.find_elements(By.CLASS_NAME, 'job_seen_beacon')

            print(f'Number of cards found on the page: {len(cards)}')

            records = self.get_jobs(cards)
            all_records.extend(records)

            try:
                next_button = WebDriverWait(browser, 10).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//a[@data-testid='pagination-page-next']"))
                )

                if next_button.is_enabled():
                    WebDriverWait(browser, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//a[@data-testid='pagination-page-next']"))
                    )
                    next_button.click()

                    WebDriverWait(browser, 10).until(
                        EC.staleness_of(cards[0])
                    )
                else:
                    print(
                        "'Next' button found, but disabled. Ending the collection.")
                    break

            except (NoSuchElementException, TimeoutException):
                print("No more pages to scroll through.")
                break

            except Exception as e:
                print(f"Error trying to advance to the next page: {e}")
                break

        print(f"Total records obtained: {len(all_records)}")
        data = [record.__dict__ for record in all_records]

        with open('jobs.json', 'w', newline='') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def get_brasilia_date_time_str(self) -> str:
        return datetime.now(timezone('America/Sao_Paulo')).strftime(DATE_TIME_FORMAT)

    def convert_to_record(self, card) -> JobRecord:
        record = JobRecord()
        url_template = "https://br.indeed.com/viewjob?jk={}"

        if isinstance(card, WebElement):
            web_element = card
        else:
            return None

        element = web_element.find_element(
            by=By.TAG_NAME,
            value="a"
        )

        record.job_source_id = element.get_attribute("data-jk")
        record.job_title = element.text

        record.job_url = url_template.format(
            record.job_source_id)

        try:
            record.company = web_element.find_element(by=By.XPATH, value='.//span[@data-testid="company-name"]').text if (
                not web_element.find_element(by=By.XPATH, value='.//span[@data-testid="company-name"]') == None) else ''
        except NoSuchElementException as e:
            print(f"Element not found: {e}")
            record.company = ''

        location = web_element.find_element(
            by=By.XPATH, value='.//div[@data-testid="text-location"]')

        if location is None:
            record.location = ''
        else:
            record.location = location.text

        record.job_date = self.get_brasilia_date_time_str()

        return record

    def get_jobs(self, cards: list) -> list:
        result = []

        for card in cards:
            record = self.convert_to_record(card)

            if not record is None:
                result.append(record)

        return result


if __name__ == '__main__':
    # url = 'https://br.indeed.com/jobs?q=desenvolvedor+python&l=Remoto'
    url = "https://br.indeed.com/jobs?q=desenvolvedor+python&l=Remoto&fromage=1"
    bot = Bot(url)
    bot.get_scrape_data()
