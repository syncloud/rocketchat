import json
import os
import sys
from os import listdir
from os.path import dirname, join, exists, abspath, isdir
import time
from subprocess import check_output
import pytest
import shutil

from integration.util.loop import loop_device_add, loop_device_cleanup
from integration.util.ssh import run_scp, run_ssh
from integration.util.helper import local_install, wait_for_rest
app_path = join(dirname(__file__), '..')
sys.path.append(join(app_path, 'src'))

lib_path = join(app_path, 'lib')
libs = [abspath(join(lib_path, item)) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(lambda x: sys.path.append(x), libs)

import requests


SYNCLOUD_INFO = 'syncloud.info'
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
DEFAULT_DEVICE_PASSWORD = 'syncloud'
LOGS_SSH_PASSWORD = DEFAULT_DEVICE_PASSWORD
DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')

SAM_PLATFORM_DATA_DIR='/opt/data/platform'
SNAPD_PLATFORM_DATA_DIR='/var/snap/platform/common'
DATA_DIR=''

SAM_DATA_DIR='/opt/data/rocketchat'
SNAPD_DATA_DIR='/var/snap/rocketcaht/common'
DATA_DIR=''

SAM_APP_DIR='/opt/app/rocketcaht'
SNAPD_APP_DIR='/snap/rocketcaht/current'
APP_DIR=''


@pytest.fixture(scope="session")
def platform_data_dir(installer):
    if installer == 'sam':
        return SAM_PLATFORM_DATA_DIR
    else:
        return SNAPD_PLATFORM_DATA_DIR
        

@pytest.fixture(scope="session")
def data_dir(installer):
    if installer == 'sam':
        return SAM_DATA_DIR
    else:
        return SNAPD_DATA_DIR


@pytest.fixture(scope="session")
def app_dir(installer):
    if installer == 'sam':
        return SAM_APP_DIR
    else:
        return SNAPD_APP_DIR


@pytest.fixture(scope="session")
def service_prefix(installer):
    if installer == 'sam':
        return ''
    else:
        return 'snap.'


@pytest.fixture(scope="session")
def ssh_env_vars(installer):
    if installer == 'sam':
        return ''
    if installer == 'snapd':
        return 'SNAP_COMMON={0} '.format(SNAPD_DATA_DIR)


@pytest.fixture(scope="session")
def module_setup(request, device_host, data_dir, platform_data_dir, app_dir):
    request.addfinalizer(lambda: module_teardown(device_host, data_dir, platform_data_dir, app_dir))


def module_teardown(device_host, data_dir, platform_data_dir, app_dir):
    platform_log_dir = join(LOG_DIR, 'platform_log')
    os.mkdir(platform_log_dir)
    run_scp('root@{0}:{1}/log/* {2}'.format(device_host, platform_data_dir, platform_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    
    run_scp('root@{0}:/var/log/sam.log {1}'.format(device_host, platform_log_dir), password=LOGS_SSH_PASSWORD, throw=False)

    run_ssh(device_host, 'top -bn 1 -w 500 -c > {0}/log/top.log'.format(data_dir), password=LOGS_SSH_PASSWORD)
    run_ssh(device_host, 'ps auxfw > {0}/log/ps.log'.format(data_dir), password=LOGS_SSH_PASSWORD)
    run_ssh(device_host, 'systemctl status rocketchat-server > {0}/log/rocketchat.status.log'.format(data_dir), password=LOGS_SSH_PASSWORD)
    run_ssh(device_host, 'netstat -nlp > {0}/log/netstat.log'.format(data_dir), password=LOGS_SSH_PASSWORD)
    run_ssh(device_host, 'journalctl | tail -500 > {0}/log/journalctl.log'.format(data_dir), password=LOGS_SSH_PASSWORD)
    run_ssh(device_host, 'tail -500 /var/log/syslog > {0}/log/syslog.log'.format(data_dir), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'tail -500 /var/log/messages > {0}/log/messages.log'.format(data_dir), password=LOGS_SSH_PASSWORD, throw=False)

    app_log_dir  = join(LOG_DIR, 'rocketcaht_log')
    os.mkdir(app_log_dir )
    run_scp('root@{0}:{1}/log/*.log {2}'.format(device_host, data_dir, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)


@pytest.fixture(scope='function')
def syncloud_session(device_host):
    session = requests.session()
    session.post('http://{0}/rest/login'.format(device_host), data={'name': DEVICE_USER, 'password': DEVICE_PASSWORD})
    return session


@pytest.fixture(scope='function')
def rocketcaht_session_domain(user_domain, device_host):
    session = requests.session()
    response = session.get('http://{0}'.format(user_domain), allow_redirects=True)
    print(response.text)
    # soup = BeautifulSoup(response.text, "html.parser")
    # requesttoken = soup.find_all('input', {'name': 'requesttoken'})[0]['value']
    # response = session.post('http://{0}/index.php/login'.format(device_host),
    #                         headers={"Host": user_domain},
    #                         data={'user': DEVICE_USER, 'password': DEVICE_PASSWORD, 'requesttoken': requesttoken},
    #                         allow_redirects=False)
    # assert response.status_code == 303, response.text
    return session
#


def test_start(module_setup):
    shutil.rmtree(LOG_DIR, ignore_errors=True)
    os.mkdir(LOG_DIR)


def test_activate_device(auth, device_host):
    email, password, domain, release = auth

    response = requests.post('http://{0}:81/rest/activate'.format(device_host),
                             data={'main_domain': SYNCLOUD_INFO, 'redirect_email': email, 'redirect_password': password,
                                   'user_domain': domain, 'device_username': DEVICE_USER, 'device_password': DEVICE_PASSWORD})
    assert response.status_code == 200, response.text
    global LOGS_SSH_PASSWORD
    LOGS_SSH_PASSWORD = DEVICE_PASSWORD


# def test_enable_external_access(syncloud_session, device_host):
#     response = syncloud_session.get('http://{0}/server/rest/settings/set_protocol'.format(device_host), params={'protocol': 'https'})
#     assert '"success": true' in response.text
#     assert response.status_code == 200


def test_install(app_archive_path, device_host, installer, user_domain):
    local_install(device_host, DEVICE_PASSWORD, app_archive_path, installer)
    wait_for_rest(requests.session(), user_domain, '/', 200, 50)


def test_remove(syncloud_session, device_host):
    response = syncloud_session.get('http://{0}/rest/remove?app_id=rocketcaht'.format(device_host), allow_redirects=False)
    assert response.status_code == 200, response.text


#def test_reinstall(app_archive_path, device_host, installer):
#    local_install(device_host, DEVICE_PASSWORD, app_archive_path, installer)