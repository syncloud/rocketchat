import os
from os.path import dirname, join
from subprocess import check_output

import pytest
import requests
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install, wait_for_installer

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(device, request, data_dir, platform_data_dir, artifact_dir):
    def module_teardown():
        platform_log_dir = join(artifact_dir, 'platform_log')
        os.mkdir(platform_log_dir)
        device.scp_from_device('{0}/log/*'.format(platform_data_dir), platform_log_dir, throw=False)
        device.run_ssh('mkdir {0}'.format(TMP_DIR))
        device.run_ssh('top -bn 1 -w 500 -c > {0}/top.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ps auxfw > {0}/ps.log'.format(TMP_DIR), throw=False)
        device.run_ssh('systemctl status snap.rocketchat.server > {0}/rocketchat.status.log'.format(TMP_DIR), throw=False)
        device.run_ssh('systemctl status snap.rocketchat.mongodb > {0}/mongodb.status.log'.format(TMP_DIR), throw=False)
        device.run_ssh('netstat -nlp > {0}/netstat.log'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/journalctl.log'.format(TMP_DIR), throw=False)
        device.run_ssh('cp /var/log/syslog {0}/syslog.log'.format(TMP_DIR), throw=False)
        device.run_ssh('cp /var/log/messages {0}/messages.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /snap > {0}/snap.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /snap/rocketchat > {0}/snap.rocketchat.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /var/snap/rocketchat/current/> {0}/var.current.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la /var/snap/rocketchat/common/> {0}/var.common.ls.log'.format(TMP_DIR), throw=False)
        device.run_ssh('ls -la {0}/log > {1}/data.log.dir.ls.log'.format(data_dir, TMP_DIR), throw=False)
        device.run_ssh('df -h > {0}/df.log'.format(TMP_DIR), throw=False)
        device.run_ssh('df -h > {0}/df.log'.format(TMP_DIR), throw=False)

        device.scp_from_device('{0}/config/rocketchat.env'.format(data_dir), artifact_dir)
        device.scp_from_device('{0}/*'.format(TMP_DIR), artifact_dir)
        device.scp_from_device('{0}/log/*'.format(data_dir), artifact_dir)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, device, app, domain, device_host):
    add_host_alias(app, device_host, domain)
    device.run_ssh('date', retries=100, throw=True)


def test_activate_device(device):
    response = device.activate_custom()
    assert response.status_code == 200, response.text


def test_install(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)
    

def test_remove(device, app):
    response = device.app_remove(app)
    assert response.status_code == 200, response.text

# TODO: restore this test after first stable arm64 store release
# def test_latest_from_store(device):
#     device.run_ssh('snap install rocketchat')


def test_upgrade(app_archive_path, device_host, device_password):
    local_install(device_host, device_password, app_archive_path)


def test_mongo_config(device, app_dir, data_dir):
    device.scp_to_device('{0}/mongodb.config.dump.js'.format(DIR), '/')
    device.run_ssh(
        '{0}/mongodb/bin/mongo.sh /mongodb.config.dump.js > {1}/log/mongo.config.dump.log'.format(app_dir, data_dir),
        throw=False)


def test_storage_change(device, app_dir, data_dir):
    device.run_ssh('snap run rocketchat.storage-change > {1}/log/storage-change.log'.format(app_dir, data_dir),
                   throw=False)
