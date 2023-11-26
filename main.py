import time
import subprocess
import os
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from PIL import Image

class LescoBillScraper:
    def __init__(self, customer_ids):
        self.URL = 'http://www.lesco.gov.pk:36269/Modules/CustomerBill/CheckBill.asp'
        self.IMAGE_NAME = 'captcha_image.png'
        self.customer_ids = customer_ids
        self.chrome_options = self.setup_chrome_options()

    def setup_chrome_options(self):
        chromium_path = subprocess.check_output(['which', 'chromium']).decode('utf-8').strip()
        options = webdriver.ChromeOptions()
        options.binary_location = chromium_path
        # options.add_argument('--headless')
        options.add_argument('--kiosk-printing')
        return options

    def capture_captcha(self, driver, customer_id):
        driver.find_element(By.NAME, 'form2').find_element(By.NAME, 'txtCustID').send_keys(customer_id)
        driver.find_element(By.NAME, 'form2').find_element(By.NAME, 'btnViewMenu').click()
        time.sleep(3)
        img_element = driver.find_element(By.CSS_SELECTOR, '#ContentPane img')
        screenshot_path = self.IMAGE_NAME
        img_element.screenshot(screenshot_path)
        captcha_text = pytesseract.image_to_string(Image.open(screenshot_path))
        print(f'Text extracted from the image for customer ID {customer_id}: {captcha_text}')
        os.remove(screenshot_path)
        return captcha_text

    def perform_actions(self, driver, captcha_text):
        input_field = driver.find_element(By.CLASS_NAME, 'billform').find_element(By.NAME, 'code')
        input_field.send_keys(captcha_text)
        time.sleep(3)
        html_content = driver.page_source
        # driver.save_screenshot('final_screenshot.png')

        print_link = driver.find_element(By.CSS_SELECTOR, '#printPageButton a')
        print_link.click()
        time.sleep(3)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ENTER)
        time.sleep(3)

    def run_scraper(self):
        for customer_id in self.customer_ids:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(self.URL)

            captcha_text = self.capture_captcha(driver, customer_id)
            self.perform_actions(driver, captcha_text)

            driver.quit()

if __name__ == "__main__":
    customer_ids = ['1','2','3']
    scraper = LescoBillScraper(customer_ids)
    scraper.run_scraper()
