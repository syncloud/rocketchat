import json
import logging
import uuid
from os import path
from os.path import join
from subprocess import check_output, CalledProcessError

import requests
from syncloudlib import fs, linux, gen, logger
from syncloudlib.application import urls, storage
from syncloudlib.http import wait_for_rest

APP_NAME = 'rocketchat'
USER_NAME = 'rocketchat'
PORT = 3000
MONGODB_PORT = 27017
REST_URL = "http://localhost:{0}/api/v1".format(PORT)


class Installer:
    def __init__(self):
        if not logger.factory_instance:
            logger.init(logging.DEBUG, True)

        self.log = logger.get_logger('rocketchat')
        self.snap_dir = '/snap/rocketchat/current'
        self.data_dir = '/var/snap/rocketchat/current'
        self.common_dir = '/var/snap/rocketchat/common'
        self.app_url = urls.get_app_url(APP_NAME)
        self.install_file = join(self.common_dir, 'installed')
        self.database_dump = join(self.data_dir, 'database.dump.gzip')
        self.rocketchat_env_file_source = join(self.snap_dir, 'config', 'rocketchat.env')
        self.rocketchat_env_file_target = join(self.data_dir, 'config', 'rocketchat.env')

    def pre_refresh(self):
        try:
            self.log.info(check_output('rm -rf {0}'.format(self.database_dump), shell=True))
            self.log.info(
                check_output(
                    '{0}/mongodb/bin/mongodump.sh --archive={1} --gzip'.format(self.snap_dir, self.database_dump),
                    shell=True))
            self.log.info(
                check_output('{0}/mongodb/bin/mongo.sh --eval \'db.repairDatabase()\''.format(self.snap_dir),
                             shell=True))
        except CalledProcessError as e:
            self.log.error("pre_refresh error: " + e.output.decode())
            raise e

    def post_refresh(self):
        self.log.info('post refresh')
        self.init_config()

    def install(self):
        self.log.info('install')
        self.init_config()

    def init_config(self):
        linux.useradd(USER_NAME)

        log_dir = join(self.common_dir, 'log')
        self.log.info('creating log dir: {0}'.format(log_dir))
        fs.makepath(log_dir)
        fs.makepath(join(self.data_dir, 'nginx'))
        fs.makepath(join(self.data_dir, 'mongodb'))

        gen.generate_file_jinja(self.rocketchat_env_file_source, self.rocketchat_env_file_target, {'url': self.app_url})

        fs.chownpath(self.data_dir, USER_NAME, recursive=True)
        fs.chownpath(self.common_dir, USER_NAME, recursive=True)

        self.prepare_storage()

    def configure(self):
        self.log.info('configure')
        wait_for_rest(requests.session(), REST_URL, 200, 100)

        if path.isfile(self.install_file):
            self._upgrade()
        else:
            self._install()

    def _upgrade(self):
        self.log.info('configure upgrade')
        if not path.isfile(self.database_dump):
            raise Exception('please export database manually to {0}'.format(self.database_dump))

        try:
            self.log.info(check_output(
                '{0}/mongodb/bin/mongorestore.sh --drop --archive={1} --gzip'.format(self.snap_dir,
                                                                                     self.database_dump),
                shell=True))
        except CalledProcessError as e:
            self.log.error("upgrade error: " + e.output.decode())
            raise e

    def _install(self):
        self.log.info('configure install')
        password = uuid.uuid4().hex
        response = requests.post("{0}/users.register".format(REST_URL),
                                 json={
                                     "username": "installer",
                                     "email": "installer@example.com",
                                     "pass": password,
                                     "name": "installer"})

        result = json.loads(response.text)
        if not result['success']:
            self.log.info('response: {0}'.format(response.text.encode("utf-8")))
            raise Exception('cannot create install account')

        self.log.info('install account has been created')

        response = requests.post("{0}/login".format(REST_URL), json={"username": "installer", "password": password})
        result = json.loads(response.text)
        if not result['status'] == 'success':
            self.log.error(response.text.encode("utf-8"))
            self.log.info(result['status'])
            raise Exception('unable to login under install user')

        auth_token = result['data']['authToken']
        user_id = result['data']['userId']
        self.log.info('install account token extracted')

        self.update_setting('LDAP_Enable', True, auth_token, user_id)
        #v4 self.update_setting('LDAP_Server_Type', '', auth_token, user_id)
        self.update_setting('LDAP_Host', 'localhost', auth_token, user_id)
        self.update_setting('LDAP_BaseDN', 'dc=syncloud,dc=org', auth_token, user_id)
        self.update_setting('LDAP_Authentication', True, auth_token, user_id)
        self.update_setting('LDAP_Authentication_UserDN', 'dc=syncloud,dc=org', auth_token, user_id)
        self.update_setting('LDAP_Authentication_Password', 'syncloud', auth_token, user_id)
        self.update_setting('LDAP_User_Search_Filter', '(objectclass=inetOrgPerson)', auth_token, user_id)
        self.update_setting('LDAP_User_Search_Field', 'cn', auth_token, user_id)
        self.update_setting('LDAP_Username_Field', 'cn', auth_token, user_id)
        self.update_setting('Accounts_RegistrationForm', 'Disabled', auth_token, user_id)
        #v4 self.update_setting('Accounts_TwoFactorAuthentication_Enabled', False, auth_token, user_id)
        self.update_setting('Show_Setup_Wizard', 'completed', auth_token, user_id)

        self.update_setting('FileUpload_Storage_Type', 'FileSystem', auth_token, user_id)

        app_storage_dir = storage.init_storage(APP_NAME, USER_NAME)

        self.update_setting('FileUpload_FileSystemPath', app_storage_dir, auth_token, user_id)

        response = requests.post("{0}/users.delete".format(REST_URL),
                                 headers={"X-Auth-Token": auth_token, "X-User-Id": user_id},
                                 json={"userId": user_id})
        result = json.loads(response.text)
        if not result['success']:
            self.log.error(response.text.encode("utf-8"))
            raise Exception('unable to delete install user')

        with open(self.install_file, 'w') as f:
            f.write('installed\n')

    def update_setting(self, name, value, auth_token, user_id):

        response = requests.post("{0}/settings/{1}".format(REST_URL, name),
                                 headers={"X-Auth-Token": auth_token, "X-User-Id": user_id},
                                 json={"value": value})
        result = json.loads(response.text)
        if not result['success']:
            self.log.info('cannot update setting: {0}'.format(name))
            self.log.info('response: {0}'.format(response.text.encode("utf-8")))
            raise Exception('unable to update settings')

    def prepare_storage(self):
        app_storage_dir = storage.init_storage(APP_NAME, USER_NAME)
        return app_storage_dir
