import pytest
import time
from os.path import dirname, join
from subprocess import check_output
from syncloudlib.integration.hosts import add_host_alias
from integration.lib import login_4, login_5

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud/ui'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir, ui_mode):
    def module_teardown():
        device.activated()
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR, ui_mode), throw=False)
        device.run_ssh('cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR, ui_mode), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), join(artifact_dir, ui_mode))
        check_output('cp /videos/* {0}'.format(artifact_dir), shell=True)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, domain, device_host):
    add_host_alias(app, device_host, domain)


def test_login(selenium, device_user, device_password):
    login_5(selenium, device_user, device_password)
 

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

    save = selenium.find_by_xpath("//button[text()='Save changes']")
    save.click()
    
    time.sleep(10)

    selenium.screenshot('profile-new-picture')


#def test_channel(selenium, app_domain):
#    selenium.driver.get("https://{0}/channel/general".format(app_domain))
#    selenium.find_by_xpath("//*[text()='Start of conversation']")
#    selenium.screenshot('channel')


def test_teardown(driver):
    driver.quit()
