import pytest
import time
from os.path import dirname, join
from subprocess import check_output
from syncloudlib.integration.hosts import add_host_alias
from test.lib import login_6, admin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud/ui'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode, selenium):
    def module_teardown():
        device.activated()
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR, ui_mode), throw=False)
        device.run_ssh('cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR, ui_mode), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, ui_mode))
        check_output('cp /videos/* {0}'.format(artifact_dir), shell=True)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)
        selenium.log()

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, domain, device_host):
    add_host_alias(app, device_host, domain)


def test_login(selenium, device_user, device_password):
    login_6(selenium, device_user, device_password)


def test_setup(selenium, app_domain):
    #selenium.screenshot('setup-wizard-1')
    #select = Select(selenium.find_by(By.NAME, 'Organization_Type'))
    #select.select_by_visible_text('Community')
    
    selenium.screenshot('setup-wizard-2')
    anme = selenium.find_by(By.NAME, 'organizationName')
    anme.send_keys('Syncloud')
    
    selenium.screenshot('setup-wizard-3')
    selenium.find_by(By.XPATH, "//button[@name='organizationIndustry']").click()
    selenium.find_by(By.XPATH, "//div[.='Education']").click()
    
    selenium.find_by(By.XPATH, "//button[@name='organizationSize']").click()
    selenium.find_by(By.XPATH, "//div[.='1-10 people']").click()

    selenium.find_by(By.XPATH, "//button[@name='country']").click()
    selenium.find_by(By.XPATH, "//div[.='Albania']").click()
    
    selenium.screenshot( 'setup-wizard-4-next')
    selenium.find_by(By.XPATH, '//span[.="Next"]').click()
    
    selenium.screenshot( 'setup-wizard-5-email')
    email = selenium.find_by(By.XPATH, "//input[@name='email']")
    email.send_keys('test@example.com')
    
    selenium.screenshot( 'setup-wizard-6-agreement')
    selenium.find_by(By.XPATH, "//label[contains(@class, 'rcx-check-box')]").click()
 
    selenium.screenshot( 'setup-wizard-7-register')
    selenium.find_by(By.XPATH, "//span[.='Register workspace']").click()
    
    selenium.screenshot( 'setup-wizard-7-finish')
    #selenium.find_by(By.CSS_SELECTOR, '.setup-wizard-forms__content-register-radio-text').click()
    #selenium.find_by(By.CSS_SELECTOR, '.setup-wizard-forms__footer-next').click()
    device.run_ssh('/snap/rocketchat/current/bin/disable-wizard.sh')
    selenium.driver.get("https://{0}".format(app_domain))

def test_admin(selenium):
    admin(selenium)


def test_profile(selenium, app_domain):
    selenium.driver.get("https://{0}/account/profile".format(app_domain))
    selenium.screenshot('profile')
    username = selenium.find_by_xpath("//div/label[text()='Name']/following-sibling::span/input")
    username.send_keys('Syncloud user')
    
    profile_file = 'input[type="file"]'
    selenium.driver.execute_script("document.querySelector('{0}').style.display='block';".format(profile_file))
    profile_file = selenium.find_by_css(profile_file)
    profile_file.send_keys(join(DIR, 'images', 'profile.jpeg'))
    
    #email = selenium.find_by_xpath("//div/label[text()='Email']/following-sibling::span/label/input")
    #email.clear()
    #email.send_keys('test@gmail.com')

    selenium.screenshot('profile-new-name')

    save = selenium.find_by_xpath("//span[text()='Save changes']")
    save.click()
    
    time.sleep(10)

    selenium.screenshot('profile-new-picture')


#def test_channel(selenium, app_domain):
#    selenium.driver.get("https://{0}/channel/general".format(app_domain))
#    selenium.find_by_xpath("//*[text()='Start of conversation']")
#    selenium.screenshot('channel')
