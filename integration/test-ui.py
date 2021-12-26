import pytest
import time
from os.path import dirname, join
from selenium.webdriver.common.keys import Keys
from subprocess import check_output
from syncloudlib.integration.hosts import add_host_alias

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


def test_start(module_setup, app, domain, device_host):
    add_host_alias(app, device_host, domain)


def test_index(selenium):
    selenium.open_app()
    selenium.screenshot('index')


def test_login(selenium, device_user, device_password):

    # wait_driver = WebDriverWait(driver, 120)
    # wait_driver.until(EC.element_to_be_clickable((By.ID, 'emailOrUsername')))

    user = selenium.find_by_id("emailOrUsername")
    user.send_keys(device_user)
    password = selenium.find_by_id("pass")
    password.send_keys(device_password)
    selenium.screenshot('login')

    password.send_keys(Keys.RETURN)
    selenium.screenshot('login_progress')
     

def test_main(selenium):
    selenium.screenshot('main')


def test_profile(selenium, app_domain):
    selenium.driver.get("https://{0}/account/profile".format(app_domain))
    app_domain.screenshot('profile')
    profile_file = 'input[type="file"]'
    # wait_or_screenshot(driver, ui_mode, screenshot_dir, EC.presence_of_element_located((By.CSS_SELECTOR, profile_file)))
    profile_file = selenium.find_by_css(profile_file)
    profile_file.send_keys(join(DIR, 'images', 'profile.jpeg'))
     
    username = selenium.find_by_xpath("//div/label[text()='Name']/following-sibling::span/input")
    username.send_keys('Syncloud user')
    
    email = selenium.find_by_xpath("//div/label[text()='Email']/following-sibling::span/label/input")
    email.clear()
    email.send_keys('test@gmail.com')

#    password = driver.find_element_by_xpath("//div/label[text()='Password']/following-sibling::span/label/input")
#    password.clear()
#    password.send_keys(device_password)

#    time.sleep(2)
    
#    confirm_password = driver.find_element_by_xpath("//div/label[text()='Confirm your password']/following-sibling::span/label/input")
#    confirm_password.send_keys(device_password)

    selenium.screenshot('profile-new-name')

    save = selenium.find_by_xpath("//button[text()='Save changes']")
    save.click()
    
    time.sleep(10)

    selenium.screenshot('profile-new-picture')


def test_channel(selenium, app_domain):
    selenium.get("https://{0}/channel/general".format(app_domain))
    time.sleep(10)
    selenium.screenshot('channel')
