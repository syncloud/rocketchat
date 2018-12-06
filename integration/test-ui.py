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


def new_profile(user_agent):
    profile = webdriver.FirefoxProfile()
    profile.add_extension('/tools/firefox/JSErrorCollector.xpi')
    profile.set_preference('app.update.auto', False)
    profile.set_preference('app.update.enabled', False)
    profile.set_preference("general.useragent.override", user_agent)

    return profile

def new_driver(profile):

    if exists(screenshot_dir):
        shutil.rmtree(screenshot_dir)
    os.mkdir(screenshot_dir)

    firefox_path = '/tools/firefox/firefox'
    caps = DesiredCapabilities.FIREFOX
    caps["marionette"] = True
    caps['acceptSslCerts'] = True

    binary = FirefoxBinary(firefox_path)

    return webdriver.Firefox(profile, capabilities=caps, log_path="{0}/firefox.log".format(LOG_DIR),
                             firefox_binary=binary, executable_path='/tools/geckodriver/geckodriver')


@pytest.fixture(scope="module")
def driver():
    profile = new_profile("Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0")
    driver = new_driver(profile)
    driver.set_window_position(0, 0)
    driver.set_window_size(1024, 768)
    return driver
    
    
@pytest.fixture(scope="module")
def mobile_driver():    
    profile = new_profile("Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16")
    driver = new_driver(profile)
    driver.set_window_position(0, 0)
    driver.set_window_size(400, 2000)
    return driver
    

def test_index(driver, app_domain):

    driver.get("https://{0}".format(app_domain))
    time.sleep(10)
    print(driver.execute_script('return window.JSErrorCollector_errors ? window.JSErrorCollector_errors.pump() : []'))
    screenshots(driver, 'index')
    print(driver.page_source.encode('utf-8'))


def test_login(driver, app_domain):

    wait_driver = WebDriverWait(driver, 120)
    wait_driver.until(EC.element_to_be_clickable((By.ID, 'emailOrUsername')))

    user = driver.find_element_by_id("emailOrUsername")
    user.send_keys(DEVICE_USER)
    password = driver.find_element_by_id("pass")
    password.send_keys(DEVICE_PASSWORD)
    screenshots(driver, 'login')

    password.send_keys(Keys.RETURN)
    screenshots(driver, 'login_progress')
    time.sleep(20)
    screenshots(driver, 'setup')
     
     
def test_setup(driver, app_domain):

    screenshots(driver, 'setup-wizard-debug-Organization_Type')
    select = Select(driver.find_element_by_name('Organization_Type'))
    select.select_by_visible_text('Community')
    
    time.sleep(2)
    screenshots(driver, 'setup-wizard-debug-Organization_Name')
    anme = driver.find_element_by_name('Organization_Name')
    anme.send_keys('Syncloud')

    time.sleep(2)
    screenshots(driver, 'setup-wizard-debug-Industry')
    select = Select(driver.find_element_by_name('Industry'))
    select.select_by_visible_text('Technology Provider')

    time.sleep(2)
    screenshots(driver, 'setup-wizard-Size')
    select = Select(driver.find_element_by_name('Size'))
    select.select_by_visible_text('4000 or more people')

    time.sleep(2)
    screenshots(driver, 'setup-wizard-debug-Country')
    select = Select(driver.find_element_by_name('Country'))
    select.select_by_visible_text('United Kingdom')

    time.sleep(2)
    screenshots(driver, 'setup-wizard-debug-Website')
    website = driver.find_element_by_name('Website')
    website.send_keys('syncloud.org')

    time.sleep(2)
    screenshots(driver, 'setup-wizard-step-1')
    driver.find_element_by_css_selector('.setup-wizard-forms__footer-next').click()
    time.sleep(10)

    screenshots(driver, 'setup-wizard-debug-site-name')
    site = driver.find_element_by_name('Site_Name')
    site.send_keys('Syncloud')

    time.sleep(2)
    screenshots(driver, 'setup-wizard-debug-Server_Type')
    select = Select(driver.find_element_by_name('Server_Type'))
    select.select_by_visible_text('Private Team')
    
    screenshots(driver, 'setup-wizard-step-2')

    driver.find_element_by_css_selector('.setup-wizard-forms__footer-next').click()
    time.sleep(10)

    screenshots(driver, 'setup-wizard-step-3')
    driver.find_element_by_css_selector('.setup-wizard-forms__content-register-radio-text').click()
    driver.find_element_by_css_selector('.setup-wizard-forms__footer-next').click()
    time.sleep(10)


def test_welcome(driver):
    
    screenshots(driver, 'welcome')
    driver.find_element_by_css_selector('.js-finish').click()
    time.sleep(30)


def test_main(driver):
    screenshots(driver, 'main')


def test_profile(driver, app_domain):
    driver.get("https://{0}/account/profile".format(app_domain))
    time.sleep(10)
    screenshots(driver, 'profile')

    profile_file = driver.find_element_by_css_selector('input[type="file"]')
    profile_file.send_keys(join(DIR, 'images', 'profile.jpeg'))
     
    username = driver.find_element_by_id('realname')
    username.send_keys('Syncloud user')
    
    email = driver.find_element_by_name('email')
    email.clear()
    email.send_keys('test@gmail.com')
   
    time.sleep(2)
    
    screenshots(driver, 'profile-new-name')

    save = driver.find_element_by_name('send')
    save.click()

    time.sleep(10)

    screenshots(driver, 'profile-new-picture')


def test_channel(driver, app_domain):
    driver.get("https://{0}/channel/general".format(app_domain))
    time.sleep(10)
    screenshots(driver, 'channel')

    
def screenshots(driver, name):
 
    driver.get_screenshot_as_file(join(screenshot_dir, '{0}.png'.format(name)))
  
    with open(join(screenshot_dir, '{0}.html.log'.format(name)), "w") as f:
        f.write(driver.page_source.encode("utf-8"))
   
    with open(join(screenshot_dir, '{0}.js.log'.format(name)), "w") as f:
        try:
            f.write(str(driver.execute_script('return window.JSErrorCollector_errors ? window.JSErrorCollector_errors.pump() : []')))
        except WebDriverException, e:
            print("unable to get js errors: {0}".format(e))
   
