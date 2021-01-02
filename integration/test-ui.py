import time
from os.path import dirname, join
from subprocess import check_output

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.screenshots import screenshots

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud/ui'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode):
    def module_teardown():
        device.activated()
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.ui.{1}.log'.format(TMP_DIR, ui_mode), throw=False)
        device.run_ssh('cp /var/log/syslog {0}/syslog.ui.{1}.log'.format(TMP_DIR, ui_mode), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, 'log'))
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(app, device_host, module_setup):
    add_host_alias(app, device_host)


def test_index(driver, app_domain, ui_mode, screenshot_dir):

    driver.get("https://{0}".format(app_domain))
    time.sleep(10)
    print(driver.execute_script('return window.JSErrorCollector_errors ? window.JSErrorCollector_errors.pump() : []'))
    screenshots(driver, screenshot_dir, 'index-' + ui_mode)
    print(driver.page_source.encode('utf-8'))


def test_login(driver, app_domain, device_user, device_password, ui_mode, screenshot_dir):

    wait_driver = WebDriverWait(driver, 120)
    wait_driver.until(EC.element_to_be_clickable((By.ID, 'emailOrUsername')))

    user = driver.find_element_by_id("emailOrUsername")
    user.send_keys(device_user)
    password = driver.find_element_by_id("pass")
    password.send_keys(device_password)
    screenshots(driver, screenshot_dir, 'login-' + ui_mode)

    password.send_keys(Keys.RETURN)
    screenshots(driver, screenshot_dir, 'login_progress-' + ui_mode)
     

def test_main(driver, ui_mode, screenshot_dir):
    screenshots(driver, screenshot_dir, 'main-' + ui_mode)


def test_profile(driver, app_domain, device_password, ui_mode, screenshot_dir):
    driver.get("https://{0}/account/profile".format(app_domain))
    screenshots(driver, screenshot_dir, 'profile-' + ui_mode)
    profile_file = 'input[type="file"]'
    wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.CSS_SELECTOR, profile_file)))
    profile_file = driver.find_element_by_css_selector(profile_file)
    profile_file.send_keys(join(DIR, 'images', 'profile.jpeg'))
     
    username = driver.find_element_by_xpath("//div/label[text()='Name']/following-sibling::span/input")
    username.send_keys('Syncloud user')
    
    email = driver.find_element_by_xpath("//div/label[text()='Email']/following-sibling::span/label/input")
    email.clear()
    email.send_keys('test@gmail.com')

#    password = driver.find_element_by_xpath("//div/label[text()='Password']/following-sibling::span/label/input")
#    password.clear()
#    password.send_keys(device_password)

#    time.sleep(2)
    
#    confirm_password = driver.find_element_by_xpath("//div/label[text()='Confirm your password']/following-sibling::span/label/input")
#    confirm_password.send_keys(device_password)

    screenshots(driver, screenshot_dir, 'profile-new-name-' + ui_mode)

    save = driver.find_element_by_xpath("//button[text()='Save changes']")
    save.click()
    
    time.sleep(10)

    screenshots(driver, screenshot_dir, 'profile-new-picture-' + ui_mode)


def test_channel(driver, app_domain, ui_mode, screenshot_dir):
    driver.get("https://{0}/channel/general".format(app_domain))
    time.sleep(10)
    screenshots(driver, screenshot_dir, 'channel-' + ui_mode)


def wait_or_screenshot(driver, ui_mode, screenshot_dir, method):
    wait_driver = WebDriverWait(driver, 30)
    try:
        wait_driver.until(method)
    except Exception as e:
        screenshots(driver, screenshot_dir, 'exception-' + ui_mode)
        raise e
