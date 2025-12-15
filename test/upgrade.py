from subprocess import check_output

import pytest
import requests
from selenium.webdriver.common.by import By
from syncloudlib.http import wait_for_rest
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install

from test.lib import admin, send_message, read_message, login_sso, wizard_7, disable_registration, \
    register_7

TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir):
    def module_teardown():
        device.run_ssh('journalctl > {0}/upgrade.journalctl.log'.format(TMP_DIR), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), artifact_dir)
        check_output('cp /videos/* {0}'.format(artifact_dir), shell=True)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, device_host, domain, device):
    add_host_alias(app, device_host, domain)
    device.activated()
    device.run_ssh('rm -rf {0}'.format(TMP_DIR), throw=False)
    device.run_ssh('mkdir {0}'.format(TMP_DIR), throw=False)


def test_install(device, selenium, device_user, device_password, device_host, app_archive_path, app_domain, app_dir):

    device.run_ssh('snap remove rocketchat')
    device.run_ssh('snap install rocketchat')    
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)

def test_login(selenium, device_user, device_password, app_domain, device):
    selenium.open_app()
    login_sso(selenium, device_user, device_password)
    wizard_7(selenium)
    register_7(selenium)
    disable_registration(selenium, app_domain, device)


def test_upgrade(device, selenium, device_user, device_password, device_host, app_archive_path, app_domain, app_dir):

    send_message(selenium, app_domain)
    read_message(selenium, app_domain)
    
    print(device.run_ssh(
        '{0}/mongodb/bin/mongo.sh {0}/config/mongo.config.dump.js > {1}/mongo.config.old.dump.log'.format(app_dir, TMP_DIR),
        throw=False))

    local_install(device_host, device_password, app_archive_path)
    print(device.run_ssh(
        '{0}/mongodb/bin/mongo.sh {0}/config/mongo.config.dump.js > {1}/mongo.config.refresh.dump.log'.format(app_dir, TMP_DIR),
        throw=False))
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)

    selenium.open_app()

    selenium.find_by(By.XPATH, "//span[.='Register workspace']")

    selenium.screenshot('login-sso-3-done')
    
    selenium.find_by(By.XPATH, "//div[.='general']").click()
    selenium.find_by_xpath("//*[text()='Start of conversation']")
    selenium.find_by_xpath("//div[contains(.,'test message')]")

    selenium.screenshot('refresh-channel')


def test_admin(selenium):
    admin(selenium)

