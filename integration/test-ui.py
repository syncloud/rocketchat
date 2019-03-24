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
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.screenshots import screenshots


DIR = dirname(__file__)
screenshot_dir = join(DIR, 'screenshot')

def test_start(app, device_host):
    if exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    os.mkdir(screenshot_dir)

    add_host_alias(app, device_host)
    
def test_index(driver, app_domain):

    driver.get("https://{0}".format(app_domain))
    time.sleep(10)
    print(driver.execute_script('return window.JSErrorCollector_errors ? window.JSErrorCollector_errors.pump() : []'))
    screenshots(driver, screenshot_dir, 'index')
    print(driver.page_source.encode('utf-8'))


def test_login(driver, app_domain, device_user, device_password):

    wait_driver = WebDriverWait(driver, 120)
    wait_driver.until(EC.element_to_be_clickable((By.ID, 'emailOrUsername')))

    user = driver.find_element_by_id("emailOrUsername")
    user.send_keys(device_user)
    password = driver.find_element_by_id("pass")
    password.send_keys(device_password)
    screenshots(driver, screenshot_dir, 'login')

    password.send_keys(Keys.RETURN)
    screenshots(driver, screenshot_dir, 'login_progress')
    time.sleep(20)
    screenshots(driver, screenshot_dir, 'setup')
     
     
def test_setup(driver, app_domain):

    screenshots(driver, screenshot_dir, 'setup-wizard-debug-Organization_Type')
    select = Select(driver.find_element_by_name('Organization_Type'))
    select.select_by_visible_text('Community')
    
    time.sleep(2)
    screenshots(driver, screenshot_dir, 'setup-wizard-debug-Organization_Name')
    anme = driver.find_element_by_name('Organization_Name')
    anme.send_keys('Syncloud')

    time.sleep(2)
    screenshots(driver, screenshot_dir, 'setup-wizard-debug-Industry')
    select = Select(driver.find_element_by_name('Industry'))
    select.select_by_visible_text('Technology Provider')

    time.sleep(2)
    screenshots(driver, screenshot_dir, 'setup-wizard-Size')
    select = Select(driver.find_element_by_name('Size'))
    select.select_by_visible_text('4000 or more people')

    time.sleep(2)
    screenshots(driver, screenshot_dir, 'setup-wizard-debug-Country')
    select = Select(driver.find_element_by_name('Country'))
    select.select_by_visible_text('United Kingdom')

    time.sleep(2)
    screenshots(driver, screenshot_dir, 'setup-wizard-debug-Website')
    website = driver.find_element_by_name('Website')
    website.send_keys('syncloud.org')

    time.sleep(2)
    screenshots(driver, screenshot_dir, 'setup-wizard-step-1')
    driver.find_element_by_css_selector('.setup-wizard-forms__footer-next').click()
    time.sleep(10)

    screenshots(driver, screenshot_dir, 'setup-wizard-debug-site-name')
    site = driver.find_element_by_name('Site_Name')
    site.send_keys('Syncloud')

    time.sleep(2)
    screenshots(driver, screenshot_dir, 'setup-wizard-debug-Server_Type')
    select = Select(driver.find_element_by_name('Server_Type'))
    select.select_by_visible_text('Private Team')
    
    screenshots(driver, screenshot_dir, 'setup-wizard-step-2')

    driver.find_element_by_css_selector('.setup-wizard-forms__footer-next').click()
    time.sleep(10)

    screenshots(driver, screenshot_dir, 'setup-wizard-step-3')
    driver.find_element_by_css_selector('.setup-wizard-forms__content-register-radio-text').click()
    driver.find_element_by_css_selector('.setup-wizard-forms__footer-next').click()
    time.sleep(10)


def test_welcome(driver):
    
    screenshots(driver, screenshot_dir, 'welcome')
    driver.find_element_by_css_selector('.js-finish').click()
    time.sleep(30)


def test_main(driver):
    screenshots(driver, screenshot_dir, 'main')


def test_profile(driver, app_domain, device_password):
    driver.get("https://{0}/account/profile".format(app_domain))
    time.sleep(10)
    screenshots(driver, screenshot_dir, 'profile')

    profile_file = driver.find_element_by_css_selector('input[type="file"]')
    profile_file.send_keys(join(DIR, 'images', 'profile.jpeg'))
     
    username = driver.find_element_by_id('realname')
    username.send_keys('Syncloud user')
    
    email = driver.find_element_by_name('email')
    email.clear()
    email.send_keys('test@gmail.com')
   
    time.sleep(2)
    
    screenshots(driver, screenshot_dir, 'profile-new-name')

    save = driver.find_element_by_name('send')
    save.click()

    confirm_password = driver.find_element_by_css_selector('input[name="name"][type="password"]')
    confirm_password.send_keys(device_password)
    
    confirm_save = driver.find_element_by_css_selector('input[value="Save"]')
    confirm_save.click()
    
    time.sleep(10)

    screenshots(driver, screenshot_dir, 'profile-new-picture')


def test_channel(driver, app_domain):
    driver.get("https://{0}/channel/general".format(app_domain))
    time.sleep(10)
    screenshots(driver, screenshot_dir, 'channel')

    
