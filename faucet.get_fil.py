# -*- coding: utf-8 -*-

import os
import sys
import json
import subprocess
from time import sleep
from pathlib import Path
from random import random
from datetime import datetime, date, timezone, timedelta
from time import time

# need to pip install
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def initializeDriver():

    tz_cst = timezone(timedelta(hours=8))

    print('START: {}'.format(datetime.now(tz_cst).isoformat(timespec='seconds')))
    # set virtual display via Xvfb
    print('Setting virtual window ...')
    display = Display(visible=0, size=(1024, 768))
    display.start()
    print('window start!')

    # set options
    print('reading options ...')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    #options.add_argument("--proxy-server=http://154.212.129.25:10086")
    options.add_argument('--disable-infobars')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-extensions")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    # options.add_argument('--user-data-dir=/server/profile')
    # options.add_argument("--profile-directory='{}'".format('Profile 2'))
    print('Options done!')

    # set webdriver
    print('Setting webDriver ...')
    driver = webdriver.Chrome(executable_path='/snap/bin/chromium.chromedriver', options=options)
    driver.set_window_size(1024, 768)  # for Virtualdisplay
    print('webDriver is ready!')

    return driver


def solveReCaptcha(driver):

    service_key = os.environ.get('SERVICE_KEY_2CAPCHA', '46da84c0032cd7231b0e2f8caf607553')
    google_site_key = os.environ.get('GOOGLE_SITE_KEY_CWORK', '6LeoL1saAAAAADMS0kUieXFTEIYnrLr36FQtePPm')

    driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="block";')
    url = "http://2captcha.com/in.php?key=" + service_key + "&method=userrecaptcha&googlekey=" + google_site_key + "&pageurl=" + pageurl + "&invisible=1&json=1" +"&cookies=_GRECAPTCHA:09AG0dS7vT7gF2IG3ag5-xsNm6W5Rri2u4uEIU1TSnRyc0cHi5gJlFctJSJhecW7aE7HGxH3IllzuQDth6vwDu4ng"
    resp = requests.post(url) 
    state=json.loads(resp.text).get('status')
    if state != 1: 
        quit('Service error. Error code:' + resp.text) 
    captcha_id = json.loads(resp.text).get('request')

    # Make a 15-20 seconds timeout then submit a HTTP GET request to our API URL: https://2captcha.com/res.php to get the result.
    sleep(10)
    fetch_url = "http://2captcha.com/res.php?key=" + service_key + "&action=get&id=" + captcha_id + "&json=1"

    for i in range(1, 50):
        sleep(5) # wait 5 sec.
        resp = requests.get(fetch_url)
        state=json.loads(resp.text).get('status')
        if state == 1:
            print('  fetch OK.')
            break
    print(resp.text)
    captcha_code = json.loads(resp.text).get('request')
    print('Google response token: ', captcha_code)

    return captcha_code


def workerService(pageurl, driver):

    # config from ENVIRONMENT
    address = os.environ.get('ADDRESS_CWORK', 't3tcnwqzq7ur6elf244e7zsagcmmknqbquq2ubknyzhnvwfo36mzcn35meb3mfiuk4jemj4mpa2cd3tgajd36a')

    driver.get(pageurl)
    sleep(10 * random())

    soup = BeautifulSoup(driver.page_source, 'lxml')

    driver.find_element(By.NAME, value='address').send_keys(address)
    sleep(10 * random())
    
    captcha_code = solveReCaptcha(driver)
    driver.execute_script('var element=document.getElementById("g-recaptcha-response"); element.style.display="block";')
    driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = arguments[0]', captcha_code)
    sleep(10 * random())

    print(driver.page_source)
    sendButton = driver.find_element(By.XPATH, value='//*[@id="funds-form"]/button')
    driver.execute_script("arguments[0].click();", sendButton)
    sleep(10 * random())

    print(driver.current_url)
    print(driver.page_source)
    return driver


tz_cst = timezone(timedelta(hours=8))

print('ADDRESS_CWORK: {}'.format(os.environ.get('ADDRESS_CWORK', 'ENV is not configured!')))
pageurl = 'https://faucet.calibration.fildev.network/funds.html'
driver = initializeDriver()

for _ in range(50):
    try:
        workerService(pageurl, driver)
        print('execute success.', file=sys.stderr)
        break
    except requests.exceptions.ConnectionError as cne:
        print('CALL EXCEPTION ! : {}'.format(str(cne)), file=sys.stderr)
        continue

try:
    driver.quit()
    print('Driver has stopped.\n')
except NameError as ne:
    print(str(ne), file=sys.stderr)
