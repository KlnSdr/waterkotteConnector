from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from datetime import date
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

WATERKOTTE_URL = os.getenv("WATERKOTTE_URL")
WATERKOTTE_USERNAME = os.getenv("WATERKOTTE_USERNAME")
WATERKOTTE_PASSWORD = os.getenv("WATERKOTTE_PASSWORD")
AEOLUS_URL = os.getenv("AEOLUS_URL")
AEOLUS_ACCESS_TOKEN = os.getenv("AEOLUS_ACCESS_TOKEN")
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH")
PAGE_LOAD_TIMEOUT = os.getenv("PAGE_LOAD_TIMEOUT")

if WATERKOTTE_URL is None or WATERKOTTE_USERNAME is None or WATERKOTTE_PASSWORD is None or AEOLUS_URL is None or AEOLUS_ACCESS_TOKEN is None or CHROME_DRIVER_PATH is None or PAGE_LOAD_TIMEOUT is None:
    raise RuntimeError("config incomplete/missing")

# =========================================================
def uploadReading(date, value, url, accessToken):
    data = {
        "date": date,
        "value": value
    }
    json_data = json.dumps(data)
    headers = {
        "Content-Type": "application/json",
        "Hades-Login-Token": accessToken
    }
    response = requests.post(url + "/rest/readings", data=json_data, headers=headers)

    if response.status_code != 201:
        raise RuntimeError("Could not upload reading")
    pass

# =========================================================

options = Options()
options.add_argument("--headless")

service = Service(options=options, executable_path=CHROME_DRIVER_PATH)

driver = webdriver.Chrome(service=service)

try:
    driver.set_page_load_timeout(int(PAGE_LOAD_TIMEOUT))
    driver.get(WATERKOTTE_URL)

    # ==============================
    usernameFieldId = "username"
    passwordFieldId = "passwd"
    loginBttnId = "btnOK"
    temperaturTabId = "lnkMValues"
    averageTempId = "mA3"

    usernameField = driver.find_element(By.ID, usernameFieldId)
    passwordField = driver.find_element(By.ID, passwordFieldId)
    loginBttn = driver.find_element(By.ID, loginBttnId)

    usernameField.send_keys(WATERKOTTE_USERNAME)
    passwordField.send_keys(WATERKOTTE_PASSWORD)
    loginBttn.click()

    temperaturTab = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, temperaturTabId))
    )
    print('Successfully logged in')
    temperaturTab.click();

    averageTempElement = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, averageTempId))
    )

    time.sleep(3)
    
    averageTemp = averageTempElement.text
    if len(averageTemp) < 4:
        raise ValueError("no value found")
    averageTemp = averageTemp.replace(" °C", "")

    current_date = date.today()
    # Format the current date
    formatted_date = current_date.strftime("%Y-%m-%d")

    print(formatted_date + ": " + averageTemp + "°C")

    uploadReading(formatted_date, averageTemp, AEOLUS_URL, AEOLUS_ACCESS_TOKEN)
    
finally:
    driver.quit()
