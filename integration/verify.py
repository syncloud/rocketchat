import os
import shutil
from os.path import dirname, join
from subprocess import check_output

import pytest
import requests
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install
from syncloudlib.integration.ssh import run_scp, run_ssh
from syncloudlib.http import wait_for_rest
DEFAULT_DEVICE_PASSWORD = 'syncloud'
LOGS_SSH_PASSWORD = DEFAULT_DEVICE_PASSWORD
DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(device, request, data_dir, platform_data_dir, app_dir, log_dir, artifact_dir):
    def module_teardown():
        platform_log_dir = join(log_dir, 'platform_log')
        os.mkdir(platform_log_dir)
        device.scp_from_device('{0}/log/*'.format(platform_data_dir), platform_log_dir, throw=False)
        device.run_ssh('mkdir {0}'.format(TMP_DIR))
        device.run_ssh('top -bn 1 -w 500 -c > {0}/top.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ps auxfw > {0}/ps.log'.format(TMP_DIR), throw=False)
        device.run_ssh('systemctl status rocketchat-server > {0}/rocketchat.status.log'.format(TMP_DIR), throw=False)
        device.run_ssh('netstat -nlp > {0}/netstat.log'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR), throw=False)
        device.run_ssh('cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR), throw=False)
        device.run_ssh('cp /var/log/messages {0}/messages.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /snap > {0}/snap.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /snap/rocketchat > {0}/snap.rocketchat.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la {0} > {1}/data.dir.ls.log'.format(data_dir, TMP_DIR), throw=False)
        device.run_ssh('df -h > {0}/df.log'.format(TMP_DIR), throw=False)

        device.scp_from_device('{0}/config/rocketchat.env'.format(data_dir), artifact_dir)
        device.scp_from_device('{0}/*'.format(TMP_DIR), artifact_dir)
        device.scp_from_device('{0}/log/*'.format(data_dir), artifact_dir)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


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


def test_start(module_setup, device, device_host, app, log_dir):
    shutil.rmtree(log_dir, ignore_errors=True)
    os.mkdir(log_dir)
    add_host_alias(app, device_host)
    print(check_output('date', shell=True))
    run_ssh(device_host, 'date')


def test_activate_device(device):
    response = device.activate()
    assert response.status_code == 200, response.text


def test_install(app_archive_path, device_host, app_domain, device_password):
    local_install(device_host, device_password, app_archive_path)
    wait_for_rest(requests.session(), 'https://{0}/'.format(app_domain), 200, 500)


def test_mongo_config(device, app_dir, data_dir):
    device.scp_to_devce('{0}/mongodb.config.dump.js'.format(DIR), '/')
    device.run_ssh('{0}/mongodb/bin/mongo /mongodb.config.dump.js > {1}/log/mongo.config.dump.log'.format(app_dir, data_dir), throw=False)


def test_storage_change(device, app_dir, data_dir):
    device.run_ssh('snap run rocketchat.storage-change > {1}/log/storage-change.log'.format(app_dir, data_dir), throw=False)


def test_remove(device_session, device_host):
    response = device_session.get('https://{0}/rest/remove?app_id=rocketcaht'.format(device_host), allow_redirects=False, verify=False)
    assert response.status_code == 200, response.text


def test_reinstall(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)
