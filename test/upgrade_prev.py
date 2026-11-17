from os.path import dirname, join
from subprocess import check_output

import pytest
import requests
from syncloudlib.http import wait_for_rest
from syncloudlib.integration.hosts import add_host_alias

import snapd

DIR = dirname(__file__)
TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir):
    def module_teardown():
        device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
        device.run_ssh('journalctl > {0}/upgrade-prev.journalctl.log'.format(TMP_DIR), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), artifact_dir, throw=False)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, device_host, domain, device):
    add_host_alias(app, device_host, domain)
    device.activated()
    device.run_ssh('mkdir -p {0}'.format(TMP_DIR), throw=False)
    snapd.settle(device)


def test_install_prev(device, app, app_domain):
    device.run_ssh('snap remove {0}'.format(app), throw=False)
    device.run_ssh('snap install {0}'.format(app), retries=10)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 100)


def test_disable_setup_wizard(device):
    device.scp_to_device(join(DIR, '..', 'config', 'mongo.disable-wizard.js'), '/tmp/mongo.disable-wizard.js', throw=True)
    device.run_ssh('/snap/rocketchat/current/mongodb/bin/mongo.sh localhost/rocketchat /tmp/mongo.disable-wizard.js', retries=10)
