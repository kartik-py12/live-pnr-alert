from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import Client
import time

# Function to check PNR status using Selenium
def send_whatsapp_message(to, body):
    account_sid = "AC692010a6ab05941f12680b63892375a6"  # Replace with your Twilio account SID
    auth_token = "d7eeb6d1dcf31c36c9b7ac3e1f37c870"  # Replace with your Twilio auth token
    client = Client(account_sid, auth_token)

    from_whatsapp_number = "whatsapp:+14155238886"  # Twilio Sandbox number, replace with your Twilio number
    to_whatsapp_number = f"whatsapp:+916283286348"

    message = client.messages.create(
        body=body,
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )

def get_pnr_details_selenium(pnr):
    url = f"https://www.confirmtkt.com/pnr-status/{pnr}"

    # Use WebDriver (make sure you have it installed and the executable in your PATH)
    driver = webdriver.Chrome()

    try:
        driver.get(url)

        # Wait for the page to load (adjust wait time as needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'td.table-col.ellipsis span[data-bind="text: BookingStatus"]')))

        # Identify the common parent element for all seats (tbody)
        parent_element = driver.find_element(By.CSS_SELECTOR, 'tbody[data-bind="foreach: passengers"]')

        # Find all child elements (tr) within the parent element
        seat_elements = parent_element.find_elements(By.TAG_NAME, 'tr')

        # Extract details for each seat
        seat_details = []
        for seat_element in seat_elements:
            number = seat_element.find_element(By.CSS_SELECTOR, 'td.table-col.ellipsis span[data-bind="text: Number"]').text.strip()
            status = seat_element.find_element(By.CSS_SELECTOR, 'td.table-col.ellipsis span[data-bind="text: BookingStatus"]').text.strip()
            prediction = seat_element.find_element(By.CSS_SELECTOR, 'td.table-col.ellipsis span[data-bind="text: Prediction"]').text.strip()

            seat_details.append({
                'number': number,
                'status': status,
                'prediction': prediction
            })

        return seat_details
    finally:
        # Close the WebDriver
        driver.quit()

# Function to make a call using Twilio
def make_twilio_call(to, body):
    account_sid = "AC692010a6ab05941f12680b63892375a6"  # Replace with your Twilio account SID
    auth_token = "d7eeb6d1dcf31c36c9b7ac3e1f37c870"  # Replace with your Twilio auth token
    client = Client(account_sid, auth_token)

    from_twilio_number = "+14052469779"  # Twilio Sandbox number, replace with your Twilio number
    to_phone_number = "+916283286348"  # Replace with your phone number

    call = client.calls.create(
        url='https://demo.twilio.com/welcome/voice/',  # Replace with a TwiML URL or leave it as is for a sample message
        to=to_phone_number,
        from_=from_twilio_number
    )

def get_chart_prepared_status(pnr):
    url = f"https://www.confirmtkt.com/pnr-status/{pnr}"

    # Use WebDriver (make sure you have it installed and the executable in your PATH)
    driver = webdriver.Chrome()

    try:
        driver.get(url)

        # Wait for the page to load (adjust wait time as needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pas-chart')))

        # Find the div element and extract its text content
        chart_element = driver.find_element(By.CSS_SELECTOR, 'div.pas-chart')
        chart_status = chart_element.text.strip()

        return chart_status
    finally:
        # Close the WebDriver
        driver.quit()


# Your PNR number
pnr_number = "8708817981"

# Set the interval to check the PNR status (in seconds)
check_interval = 60   # Check every 5 minutes

# Initialize the previous status

while True:
    status = get_pnr_details_selenium(pnr_number)
    chart_status = get_chart_prepared_status(pnr_number)

    if chart_status == 'Chart Prepared':
        chart_message = f"Chart for PNR {pnr_number} is now prepared!"
        send_whatsapp_message("your_phone_number", chart_message)
        print('Chart Prepared!')


    for i in status:
        if 'W/L' not in i['status']:
            message_body = f"Your PNR {pnr_number} is confirmed! PNR Details: {i}"
            make_twilio_call("your_phone_number", message_body)
            print('ticket got confirmed ', status)
            break

        # Exit the loop if the ticket is confirmed

        # Update the previous status

    print(f"Retrying in {check_interval / 60} minutes...")
    current_time = datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    print("Current Time:", formatted_time)
    time.sleep(check_interval)
