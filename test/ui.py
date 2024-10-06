import time
from os.path import dirname, join
from subprocess import check_output

import pytest
import requests
from selenium.webdriver.common.by import By
from syncloudlib.http import wait_for_rest
from syncloudlib.integration.hosts import add_host_alias

from test.lib import admin, login_sso, send_message, read_message, disable_registration

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud/ui'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode, selenium):
    device.activated()
    def module_teardown():
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
    selenium.open_app()
    login_sso(selenium, device_user, device_password)

    
def test_setup(selenium, app_domain, device):
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
    disable_registration(selenium, app_domain, device)


def test_admin(selenium):
    admin(selenium)


def test_profile(selenium, app_domain):
    selenium.find_by_xpath("//button[@title='User menu']").click()
    selenium.find_by_xpath("//div[.='Profile']").click()
    selenium.find_by_xpath("//input[@name='username']").send_keys('Syncloud user')
    profile_file = 'input[type="file"]'
    selenium.driver.execute_script("document.querySelector('{0}').style.display='block';".format(profile_file))
    profile_file = selenium.find_by_css(profile_file)
    profile_file.send_keys(join(DIR, 'images', 'profile.jpeg'))
    selenium.screenshot('profile-new-name')
    selenium.find_by_xpath("//span[text()='Save changes']").click()
    time.sleep(2)
    selenium.screenshot('profile-new-picture')


def test_message(selenium, app_domain):
    send_message(selenium, app_domain)
    read_message(selenium, app_domain)
