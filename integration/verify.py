import json
import os
import sys
from os import listdir
from os.path import dirname, join, exists, abspath, isdir
import time
from subprocess import check_output
import pytest
import shutil

from syncloudlib.integration.installer import local_install, wait_for_sam, wait_for_rest, local_remove, \
    get_data_dir, get_app_dir, get_service_prefix, get_ssh_env_vars
from syncloudlib.integration.loop import loop_device_cleanup
from syncloudlib.integration.ssh import run_scp, run_ssh

import requests


SYNCLOUD_INFO = 'syncloud.info'
DEVICE_USER = 'user'
DEVICE_PASSWORD = 'password'
DEFAULT_DEVICE_PASSWORD = 'syncloud'
LOGS_SSH_PASSWORD = DEFAULT_DEVICE_PASSWORD
DIR = dirname(__file__)
LOG_DIR = join(DIR, 'log')
TMP_DIR = '/tmp/syncloud'

@pytest.fixture(scope="session")
def platform_data_dir(installer):
    return get_data_dir(installer, 'platform')

    
@pytest.fixture(scope="session")
def data_dir(installer):
    return get_data_dir(installer, 'rocketchat')


@pytest.fixture(scope="session")
def app_dir(installer):
    return get_app_dir(installer, 'rocketchat')
    

@pytest.fixture(scope="session")
def service_prefix(installer):
    return get_service_prefix(installer)


@pytest.fixture(scope="session")
def module_setup(request, device_host, data_dir, platform_data_dir, app_dir):
    request.addfinalizer(lambda: module_teardown(device_host, data_dir, platform_data_dir, app_dir))


def module_teardown(device_host, data_dir, platform_data_dir, app_dir):
    platform_log_dir = join(LOG_DIR, 'platform_log')
    os.mkdir(platform_log_dir)
    run_scp('root@{0}:{1}/log/* {2}'.format(device_host, platform_data_dir, platform_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    
    run_scp('root@{0}:/var/log/sam.log {1}'.format(device_host, platform_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'mkdir {0}'.format(TMP_DIR), password=LOGS_SSH_PASSWORD)
    run_ssh(device_host, 'top -bn 1 -w 500 -c > {0}/top.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'ps auxfw > {0}/ps.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'systemctl status rocketchat-server > {0}/rocketchat.status.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'netstat -nlp > {0}/netstat.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'journalctl | tail -500 > {0}/journalctl.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'tail -500 /var/log/messages > {0}/messages.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la /snap > {0}/snap.ls.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la /snap/rocketchat > {0}/snap.rocketchat.ls.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    

    app_log_dir  = join(LOG_DIR, 'rocketcaht_log')
    os.mkdir(app_log_dir )
    run_scp('root@{0}:{1}/log/*.log {2}'.format(device_host, data_dir, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    run_scp('root@{0}:{1}/*.log {2}'.format(device_host, TMP_DIR, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    
    run_scp('root@{0}:{1}/config/rocketchat.env {2}'.format(device_host, data_dir, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)


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
    wait_for_rest(requests.session(), user_domain, '/', 200, 500)


def test_mongo_config(device_host, app_dir, data_dir):
    run_scp('{0}/mongodb.config.dump.js root@{1}:/'.format(DIR, device_host), password=DEVICE_PASSWORD, throw=False)
    run_ssh(device_host, '{0}/mongodb/bin/mongo /mongodb.config.dump.js > {1}/log/mongo.config.dump.log'.format(app_dir, data_dir), password=DEVICE_PASSWORD, throw=False)


def test_remove(syncloud_session, device_host):
    response = syncloud_session.get('http://{0}/rest/remove?app_id=rocketcaht'.format(device_host), allow_redirects=False)
    assert response.status_code == 200, response.text


#def test_reinstall(app_archive_path, device_host, installer):
#    local_install(device_host, DEVICE_PASSWORD, app_archive_path, installer)