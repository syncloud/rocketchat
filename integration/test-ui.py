import os
import shutil
from os.path import dirname, join, exists
import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
log_dir = join(LOG_DIR, 'nextcloud_log')
screenshot_dir = join(DIR, 'screenshot')


@pytest.fixture(scope="module")
def driver():

    if exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    os.mkdir(screenshot_dir)

    firefox_path = '{0}/firefox/firefox'.format(DIR)
    caps = DesiredCapabilities.FIREFOX
    caps["marionette"] = True
    caps['acceptSslCerts'] = True

    binary = FirefoxBinary(firefox_path)

    profile = webdriver.FirefoxProfile()
    profile.add_extension('{0}/JSErrorCollector.xpi'.format(DIR))
    profile.set_preference('app.update.auto', False)
    profile.set_preference('app.update.enabled', False)
    driver = webdriver.Firefox(profile,
                               capabilities=caps, log_path="{0}/firefox.log".format(LOG_DIR),
                               firefox_binary=binary, executable_path=join(DIR, 'geckodriver/geckodriver'))
    # driver.set_page_load_timeout(30)
    # print driver.capabilities['version']
    return driver


def test_index(driver, user_domain):

    driver.get("https://{0}".format(user_domain))
    time.sleep(10)
    print(driver.execute_script('return window.JSErrorCollector_errors ? window.JSErrorCollector_errors.pump() : []'))
    screenshots(driver, screenshot_dir, 'index')
    print(driver.page_source.encode('utf-8'))


def test_login(driver, user_domain):

    wait_driver = WebDriverWait(driver, 120)
    wait_driver.until(EC.element_to_be_clickable((By.ID, 'emailOrUsername')))

    user = driver.find_element_by_id("emailOrUsername")
    user.send_keys(DEVICE_USER)
    password = driver.find_element_by_id("pass")
    password.send_keys(DEVICE_PASSWORD)
    screenshots(driver, screenshot_dir, 'login')

    password.send_keys(Keys.RETURN)
    screenshots(driver, screenshot_dir, 'login_progress')
    time.sleep(20)
    screenshots(driver, screenshot_dir, 'setup')
     
     
def test_setup(driver, user_domain):

    select = Select(driver.find_element_by_name('Organization_Type'))
    select.select_by_visible_text('Community')

    anme = driver.find_element_by_name('Organization_Name')
    anme.send_keys('Syncloud')

    select = Select(driver.find_element_by_name('Industry'))
    select.select_by_visible_text('Technology Provider')

    select = Select(driver.find_element_by_name('Size'))
    select.select_by_visible_text('4000 or more people')

    select = Select(driver.find_element_by_name('Country'))
    select.select_by_visible_text('United Kingdom')

    website = driver.find_element_by_name('Website')
    website.send_keys('syncloud.org')

    screenshots(driver, screenshot_dir, 'setup-filled')
    

def screenshots(driver, dir, name):
    desktop_w = 1024
    desktop_h = 1024
    driver.set_window_position(0, 0)
    driver.set_window_size(desktop_w, desktop_h)

    driver.get_screenshot_as_file(join(dir, '{}.png'.format(name)))

    mobile_w = 400
    mobile_h = 2000
    driver.set_window_position(0, 0)
    driver.set_window_size(mobile_w, mobile_h)
    driver.get_screenshot_as_file(join(dir, '{}-mobile.png'.format(name)))
    
    with open(join(dir, '{0}.html.log'.format(name)), "w") as f:
        f.write(driver.page_source.encode("utf-8"))
   
