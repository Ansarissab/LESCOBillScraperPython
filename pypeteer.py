import asyncio
import os
import pytesseract
from pyppeteer import launch
from PIL import Image

async def main():
    browser = await launch(headless=True, args=['--start-maximized'])
    page = await browser.newPage()

    # Navigate to the website
    await page.goto('http://www.lesco.gov.pk:36269/Modules/CustomerBill/CheckBill.asp')

    # Enter customer ID and submit
    customer_id = '1'
    await page.type('form[name="form2"] input[name="txtCustID"]', customer_id)
    await asyncio.gather(
        page.waitForNavigation(),
        page.click('form[name="form2"] input[name="btnViewMenu"]')
    )

    # Capture the image
    img_element = await page.querySelector('#ContentPane img')

    if img_element:
        bounding_box = await img_element.boundingBox()

        # Capture a screenshot of the image
        screenshot = await page.screenshot(clip={
            'x': bounding_box['x'],
            'y': bounding_box['y'],
            'width': bounding_box['width'],
            'height': bounding_box['height']
        })

        # Save the screenshot to a file
        image_path = 'captcha_image.png'
        with open(image_path, 'wb') as file:
            file.write(screenshot)

        print('Screenshot of the image captured successfully.')

        # Open the saved image with Pillow for OCR
        image = Image.open(image_path)

        # Extract text using Tesseract OCR
        captcha_text = pytesseract.image_to_string(image)
        print('Text extracted from the image:', captcha_text)

        # Remove the captured image file
        os.remove(image_path)

        # Enter captcha text and submit
        await page.type('form.billform input[name="code"]', captcha_text)
        await asyncio.gather(
            page.waitForNavigation(),
            page.click('form.billform button[type="submit"]')
        )

    else:
        print('Image not found within the specified div.')

    # Wait for navigation and capture the page content
    await page.waitForNavigation()
    html_content = await page.content()
    print(html_content)

    # Close the browser
    await browser.close()

# Run the event loop
asyncio.get_event_loop().run_until_complete(main())
