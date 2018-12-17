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
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration import conftest

import requests


DEFAULT_DEVICE_PASSWORD = 'syncloud'
LOGS_SSH_PASSWORD = DEFAULT_DEVICE_PASSWORD
DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(request, device_host, data_dir, platform_data_dir, app_dir, log_dir):
    request.addfinalizer(lambda: module_teardown(device_host, data_dir, platform_data_dir, app_dir, log_dir))


def module_teardown(device_host, data_dir, platform_data_dir, app_dir, log_dir):
    platform_log_dir = join(log_dir, 'platform_log')
    os.mkdir(platform_log_dir)
    run_scp('root@{0}:{1}/log/* {2}'.format(device_host, platform_data_dir, platform_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    
    run_ssh(device_host, 'mkdir {0}'.format(TMP_DIR), password=LOGS_SSH_PASSWORD)
    run_ssh(device_host, 'top -bn 1 -w 500 -c > {0}/top.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'ps auxfw > {0}/ps.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'systemctl status rocketchat-server > {0}/rocketchat.status.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'netstat -nlp > {0}/netstat.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'journalctl > {0}/journalctl.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)
    run_ssh(device_host, 'cp /var/log/messages {0}/messages.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la /snap > {0}/snap.ls.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    
    run_ssh(device_host, 'ls -la /snap/rocketchat > {0}/snap.rocketchat.ls.log'.format(TMP_DIR), password=LOGS_SSH_PASSWORD, throw=False)    

    app_log_dir  = join(log_dir, 'log')
    os.mkdir(app_log_dir )
    run_scp('root@{0}:{1}/log/*.log {2}'.format(device_host, data_dir, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    run_scp('root@{0}:{1}/*.log {2}'.format(device_host, TMP_DIR, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)
    
    run_scp('root@{0}:{1}/config/rocketchat.env {2}'.format(device_host, data_dir, app_log_dir), password=LOGS_SSH_PASSWORD, throw=False)


@pytest.fixture(scope='function')
def syncloud_session(device_host, device_user, device_password):
    session = requests.session()
    session.post('https://{0}/rest/login'.format(device_host), data={'name': device_user, 'password': device_password}, verify=False)
    return session


@pytest.fixture(scope='function')
def rocketcaht_session_domain(app_domain, device_host):
    session = requests.session()
    response = session.get('https://{0}'.format(app_domain), allow_redirects=True, verify=False)
    print(response.text)
    return session


def test_start(module_setup, device_host, app, log_dir):
    shutil.rmtree(log_dir, ignore_errors=True)
    os.mkdir(log_dir)
    add_host_alias(app, device_host)
    print(check_output('date', shell=True))
    run_ssh(device_host, 'date', password=LOGS_SSH_PASSWORD)


def test_activate_device(main_domain, device_host, domain, device_user, device_password, redirect_user, redirect_password):

    response = requests.post('http://{0}:81/rest/activate'.format(device_host),
                             data={'main_domain': main_domain,
                                   'redirect_email': redirect_user,
                                   'redirect_password': redirect_password,
                                   'user_domain': domain,
                                   'device_username': device_user,
                                   'device_password': device_password})
    assert response.status_code == 200, response.text
    global LOGS_SSH_PASSWORD
    LOGS_SSH_PASSWORD = device_password


def test_install(app_archive_path, device_host, app_domain, device_password):
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), app_domain, '/', 200, 500)


def test_mongo_config(device_host, app_dir, data_dir, device_password):
    run_scp('{0}/mongodb.config.dump.js root@{1}:/'.format(DIR, device_host), password=device_password, throw=False)
    run_ssh(device_host, '{0}/mongodb/bin/mongo /mongodb.config.dump.js > {1}/log/mongo.config.dump.log'.format(app_dir, data_dir), password=device_password, throw=False)

def test_storage_change(device_host, app_dir, data_dir, device_password):
    run_ssh(device_host, 'SNAP_COMMON={1} {0}/hooks/storage-change > {1}/log/storage-change.log'.format(app_dir, data_dir), password=device_password, throw=False)


def test_remove(syncloud_session, device_host):
    response = syncloud_session.get('https://{0}/rest/remove?app_id=rocketcaht'.format(device_host), allow_redirects=False, verify=False)
    assert response.status_code == 200, response.text


def test_reinstall(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)
