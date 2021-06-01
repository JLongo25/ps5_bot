from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
from datetime import datetime
import re
import requests
from ps5_helper import contact

'''

Chrome driver 84 or greater required for headless download
otherwise comment out lines 16-17 and remove options from Chrome()

'''

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument('--headless')
# For signing in, disabled Chrome from asking to save password

chrome_prefs = dict(credentials_enable_service=False, profile=dict(password_manager_enabled=False))
chrome_prefs["profile.default_content_settings"] = {"images": 2, 'popups': 1}
chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
options.experimental_options["prefs"] = chrome_prefs
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
chrome_path = '/Users/joeylongo/PycharmProjects/firstamerican_pure_pull/chromedriver'
driver = webdriver.Chrome(executable_path=chrome_path, options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
print(driver.execute_script("return navigator.userAgent;"))


def sign_in():
    driver.get('https://www.bestbuy.com/identity/global/signin')
    email = driver.find_element_by_xpath('//*[@id="fld-e"]')
    email.send_keys(contact['email'])
    password = driver.find_element_by_xpath('//*[@id="fld-p1"]')
    password.send_keys(contact['password'])
    driver.find_element_by_xpath('//button[@data-track="Sign In"]').click()
    time.sleep(2)


def search_ps5():
    headers = {"User-Agent": "Mozilla/5.0", "cache-control": "max-age=0"}
    key = 'api_key'
    sku = 6430161
    # sku = 6426149
    # sku = 6437912 #3070
    # sku = 6164543 #tester
    url = f'https://api.bestbuy.com/v1/products/{sku}.json?show=onlineAvailability,Url&apiKey={key}'
    get = requests.get(url, headers=headers)
    if 'false' in get.text:
        refresh = True
        while refresh:
            print('Sold Out - Retrying')
            time.sleep(5)
            get = requests.get(url, headers=headers)
            print(get.text)
            if 'true' in get.text:
                refresh = False

    else:
        print(f'availability: {get.text}')
    print(f'availability: {get.text}')
    cart_url = re.search("(?P<url>https?://[^\s]+)", get.text).group("url").strip('"}')
    print(f'cart_url = {cart_url}')
    return cart_url, sku


def add_to_cart(atc, sku):
    driver.get(atc)
    try:
        print('Attempting to add to cart')
        print(f'sku: {sku}')
        print(f'Product link: {atc}')
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, f'//button[@data-sku-id="{sku}"]')))
        driver.find_element_by_xpath(f'//button[@data-sku-id="{sku}"]').click()
        print('Added to cart')
    except TimeoutException:
        print('timeout')


def contact_details():
    driver.get('https://www.bestbuy.com/cart')
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, 'availability-selection')))
    curbside = driver.find_elements_by_name('availability-selection')
    curbside[0].click()
    driver.find_element_by_xpath('//button[@data-track="Checkout - Top"]').click()
    driver.get('https://www.bestbuy.com/checkout/r/payment')
    print('Checkout process started')
    print(driver.current_url)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'payment.billingAddress.firstName')))
    print('Inputting contact info')
    firstname = driver.find_element_by_id('payment.billingAddress.firstName')
    firstname.send_keys(contact['first'])
    lastname = driver.find_element_by_id('payment.billingAddress.lastName')
    lastname.send_keys(contact['last'])
    street_address = driver.find_element_by_id('payment.billingAddress.street')
    street_address.send_keys(contact['street'])
    city = driver.find_element_by_id('payment.billingAddress.city')
    city.send_keys(contact['city'])
    state = driver.find_element_by_tag_name('select')
    choose = Select(state)
    choose.select_by_value(contact['state'])
    zipcode = driver.find_element_by_id('payment.billingAddress.zipcode')
    zipcode.send_keys(contact['zip'])


def payment():
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'optimized-cc-card-number')))
    cc = driver.find_element_by_id('optimized-cc-card-number')
    cc.send_keys(contact['cc'])
    driver.find_element_by_xpath('//button[@data-track="Place your Order - Contact Card"]').click()


sign_in()
cart = search_ps5()
startTime = datetime.now()
add_to_cart(cart[0], cart[1])
contact_details()
payment()
timer = datetime.now() - startTime
print(timer.seconds)
print('done')

# https://api.bestbuy.com/v1/products/6426149.json?show=onlineAvailability,Url&apiKey=MmtH2t0aVbc4RN8QXfhrmGgz
