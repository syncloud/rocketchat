import pytest
from subprocess import check_output
from syncloudlib.integration.hosts import add_host_alias
from syncloudlib.integration.installer import local_install
from integration.lib import login
from syncloudlib.http import wait_for_rest
import requests

TMP_DIR = '/tmp/syncloud'


@pytest.fixture(scope="session")
def module_setup(request, device, artifact_dir):
    def module_teardown():
        device.run_ssh('journalctl > {0}/refresh.journalctl.log'.format(TMP_DIR), throw=False)
        device.scp_from_device('{0}/*'.format(TMP_DIR), artifact_dir)
        check_output('ls -la /video > {0}/video.log'.format(artifact_dir), shell=True)
        check_output('chmod -R a+r {0}'.format(artifact_dir), shell=True)

    request.addfinalizer(module_teardown)


def test_start(module_setup, app, device_host, domain, device):
    add_host_alias(app, device_host, domain)
    device.activated()
    device.run_ssh('rm -rf {0}'.format(TMP_DIR), throw=False)
    device.run_ssh('mkdir {0}'.format(TMP_DIR), throw=False)
    


def test_upgrade(device, arch, selenium, device_user, device_password, device_host, app_archive_path, app_domain, app_dir):
    if arch == "arm64":
        return

    device.run_ssh('snap remove rocketchat')
    device.run_ssh('snap install rocketchat')
    device.run_ssh(
        '{0}/mongodb/bin/mongo.sh /mongodb.config.dump.js > {1}/mongo.config.old.dump.log'.format(app_dir, TMP_DIR),
        throw=False)

    device.run_ssh('wget https://github.com/syncloud/3rdparty/releases/download/mongo-4.4/mongodb-amd64-4.4.tar.gz')
    device.run_ssh('tar xf mongodb-amd64-4.4.tar.gz')
    device.run_ssh('./mongodb/bin/mongodump.sh --archive=/var/snap/rocketchat/current/database.dump.gzip --gzip')

    local_install(device_host, device_password, app_archive_path)
    device.run_ssh(
        '{0}/mongodb/bin/mongo.sh /mongodb.config.dump.js > {1}/mongo.config.refresh.dump.log'.format(app_dir, TMP_DIR),
        throw=False)
    wait_for_rest(requests.session(), "https://{0}".format(app_domain), 200, 10)

    login(selenium, device_user, device_password)
