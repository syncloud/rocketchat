import pytest
from subprocess import check_output
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install
from test.lib import login_6, admin
from syncloudlib.http import wait_for_rest
from selenium.webdriver.common.keys import Keys
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


def test_upgrade(device, selenium, device_user, device_password, device_host, app_archive_path, app_domain, app_dir):

    device.run_ssh('snap remove rocketchat')
    device.run_ssh('snap install rocketchat')
    
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)
    login_6(selenium, device_user, device_password)

    admin(selenium)

    selenium.driver.get("https://{0}/channel/general".format(app_domain))
    selenium.find_by_xpath("//*[text()='Start of conversation']")
 
    selenium.find_by_xpath("//textarea[@placeholder='Message #general']").send_keys('test message')
    selenium.find_by_xpath("//textarea[@placeholder='Message #general']").send_keys(Keys.RETURN)
    selenium.find_by_xpath("//div[contains(.,'test message')]")
    selenium.screenshot('upgrade-before')

    print(device.run_ssh(
        '{0}/mongodb/bin/mongo.sh /mongodb.config.dump.js > {1}/mongo.config.old.dump.log'.format(app_dir, TMP_DIR),
        throw=False))

    local_install(device_host, device_password, app_archive_path)
    print(device.run_ssh(
        '{0}/mongodb/bin/mongo.sh /mongodb.config.dump.js > {1}/mongo.config.refresh.dump.log'.format(app_dir, TMP_DIR),
        throw=False))

    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)
    #login_4(selenium, device_user, device_password)
    selenium.driver.get("https://{0}/channel/general".format(app_domain))
    selenium.find_by_xpath("//*[text()='Start of conversation']")
    selenium.find_by_xpath("//div[contains(.,'test message')]")
    selenium.screenshot('refresh-channel')
