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
    
    def module_teardown():
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR, ui_mode), throw=False)
        device.run_ssh('cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR, ui_mode), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, ui_mode))
        check_output('cp /videos/* {0}'.format(artifact_dir), shell=True)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)
        selenium.log()

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, domain, device_host, device):
    add_host_alias(app, device_host, domain)
    device.activated()


def test_local_install(device, selenium, device_user, device_password, device_host, app_archive_path, app_domain, app_dir):

    device.run_ssh('snap remove rocketchat')
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)
    selenium.open_app()
    login_sso(selenium, device_user, device_password)
    

def test_local_upgrade(device, selenium, device_user, device_password, device_host, app_archive_path, app_domain, app_dir):

    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)
    selenium.open_app()
    login_sso(selenium, device_user, device_password)


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
