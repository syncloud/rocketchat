from subprocess import check_output

import pytest
import requests
from syncloudlib.http import wait_for_rest
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install

TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir):
    def module_teardown():
        device.run_ssh('journalctl > {0}/upgrade.journalctl.log'.format(TMP_DIR), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), artifact_dir)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, device_host, domain, device):
    add_host_alias(app, device_host, domain)
    device.activated()
    device.run_ssh('rm -rf {0}'.format(TMP_DIR), throw=False)
    device.run_ssh('mkdir {0}'.format(TMP_DIR), throw=False)


def test_install_old(device, app_domain):
    device.run_ssh('snap remove rocketchat')
    device.run_ssh('snap install rocketchat')
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)


def test_upgrade(device, device_host, device_password, app_archive_path, app_domain, app_dir):
    print(device.run_ssh(
        '{0}/mongodb/bin/mongo.sh {0}/config/mongo.config.dump.js > {1}/mongo.config.old.dump.log'.format(app_dir, TMP_DIR),
        throw=False))

    local_install(device_host, device_password, app_archive_path)

    print(device.run_ssh(
        '{0}/mongodb/bin/mongo.sh {0}/config/mongo.config.dump.js > {1}/mongo.config.refresh.dump.log'.format(app_dir, TMP_DIR),
        throw=False))
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)


def test_mongo_export_on_upgrade(device):
    device.run_ssh('ls /var/snap/rocketchat/current/database.dump.gzip')
