import pytest
from subprocess import check_output
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install
from test.lib import login_6, admin, send_message, read_message, login_sso, disable_registration, wizard_7
from syncloudlib.http import wait_for_rest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests

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

def test_login(selenium, device_user, device_password):
    selenium.open_app()
    login_sso(selenium, device_user, device_password)


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
    # login_sso(selenium, device_user, device_password)
    selenium.find_by(By.XPATH, "//div[.='Organization Info']")
    #selenium.find_by_xpath("//button[@title='User menu']")
    selenium.screenshot('login-sso-3-done')
    wizard_7(selenium, app_domain, device)
    # disable_registration(selenium, app_domain, device)
   
    #read_message(selenium, app_domain)
    selenium.find_by(By.XPATH, "//div[.='general']").click()
    selenium.find_by_xpath("//*[text()='Start of conversation']")
    selenium.find_by_xpath("//div[contains(.,'test message')]")

    selenium.screenshot('refresh-channel')


def test_admin(selenium):
    admin(selenium)


