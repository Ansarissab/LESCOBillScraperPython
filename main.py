import time
import subprocess
import os
import pytesseract
import pdfkit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from PIL import Image

URL = 'http://www.lesco.gov.pk:36269/Modules/CustomerBill/CheckBill.asp'
IMAGE_NAME = 'captcha_image.png'
customer_id = '1234'

chromium_path = subprocess.check_output(['which', 'chromium']).decode('utf-8').strip()
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = chromium_path
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--kiosk-printing')


driver = webdriver.Chrome(options=chrome_options)
driver.get(URL)

driver.find_element(By.NAME, 'form2').find_element(By.NAME, 'txtCustID').send_keys(customer_id)
driver.find_element(By.NAME, 'form2').find_element(By.NAME, 'btnViewMenu').click()
time.sleep(5)
img_element = driver.find_element(By.CSS_SELECTOR, '#ContentPane img')
screenshot_path = IMAGE_NAME
img_element.screenshot(screenshot_path)
captcha_text = ''
print('Screenshot of the image captured successfully.')
image = Image.open(screenshot_path)

text_extraction_complete = False
while not text_extraction_complete:
    try:
        captcha_text = pytesseract.image_to_string(image)
        text_extraction_complete = True
    except Exception as e:
        pass

print('Text extracted from the image:', captcha_text)
image.close()
os.remove(IMAGE_NAME)
input_field = driver.find_element(By.CLASS_NAME, 'billform').find_element(By.NAME, 'code')
input_field.send_keys(captcha_text)
time.sleep(5)
html_content = driver.page_source
# driver.save_screenshot('final_screenshot.png')

print_link = driver.find_element(By.CSS_SELECTOR, '#printPageButton a')
print_link.click()
time.sleep(5)
driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ENTER)
time.sleep(5)

driver.quit()
