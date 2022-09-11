import json
import logging
import time
import uuid
from os import path
from os.path import join
from subprocess import check_output, CalledProcessError
import shutil
import requests
from syncloudlib import fs, linux, gen, logger
from syncloudlib.application import urls, storage
from syncloudlib.http import wait_for_rest
import re
import requests_unixsocket

APP_NAME = 'rocketchat'
USER_NAME = 'rocketchat'
PORT = 3000
MONGODB_PORT = 27017
# REST_URL = "http://localhost:{0}/api/v1".format(PORT)
SUPPORTED_MAJOR_VERSION = '3.18'



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
        self.version_new_file = join(self.snap_dir, 'nodejs', 'rocketchat.version')
        self.version_old_file = join(self.data_dir, 'rocketchat.version')
        self.socket = '{0}/web.socket'.format(self.common_dir).replace('/', '%2F')
        self.base_url = 'http+unix://{0}/api/v1'.format(self.socket)


    def pre_refresh(self):
        try:
            self.log.info(check_output('rm -rf {0}'.format(self.database_dump), shell=True))
            self.log.info(
                check_output(
                    '{0}/mongodb/bin/mongodump.sh --archive={1} --gzip'.format(self.snap_dir, self.database_dump),
                    shell=True))
            # self.log.info(
            #     check_output('{0}/mongodb/bin/mongo.sh --eval \'db.repairDatabase()\''.format(self.snap_dir),
            #                  shell=True))
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
        self.check_major_version()
        wait_for_rest(requests_unixsocket.Session(), self.base_url, 200, 100)

        if path.isfile(self.install_file):
            self._upgrade()
        else:
            self._install()

    def check_major_version(self):
        if path.isfile(self.version_old_file):
            old_major = self.major_version(open(self.version_old_file).read().strip())
            new_major = self.major_version(open(self.version_new_file).read().strip())
            if old_major == SUPPORTED_MAJOR_VERSION or old_major == new_major:
                shutil.copy(self.version_new_file, self.version_old_file)
            else:
                raise Exception('cannot skip major versions, from {0} to {1}, please install {2} first'
                    .format(old_major, new_major, SUPPORTED_MAJOR_VERSION)) 

    def major_version(self, version):
        return re.match(r'(.*?\..*?)\..*', version).group(1)
     
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
        session = requests_unixsocket.Session()
        response = session.post("{0}/users.register".format(self.base_url),
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

        response = session.post("{0}/login".format(self.base_url), json={"username": "installer", "password": password})
        result = json.loads(response.text)
        if not result['status'] == 'success':
            self.log.error(response.text.encode("utf-8"))
            self.log.info(result['status'])
            raise Exception('unable to login under install user')

        auth_token = result['data']['authToken']
        user_id = result['data']['userId']
        self.log.info('install account token extracted')

        self.update_setting('LDAP_Enable', True, auth_token, user_id)
        self.update_setting('LDAP_Server_Type', '', auth_token, user_id)
        self.update_setting('LDAP_Host', 'localhost', auth_token, user_id)
        self.update_setting('LDAP_BaseDN', 'dc=syncloud,dc=org', auth_token, user_id)
        self.update_setting('LDAP_Authentication', True, auth_token, user_id)
        self.update_setting('LDAP_Authentication_UserDN', 'dc=syncloud,dc=org', auth_token, user_id)
        self.update_setting('LDAP_Authentication_Password', 'syncloud', auth_token, user_id)
        self.update_setting('LDAP_User_Search_Filter', '(objectclass=inetOrgPerson)', auth_token, user_id)
        self.update_setting('LDAP_User_Search_Field', 'cn', auth_token, user_id)
        self.update_setting('LDAP_Username_Field', 'cn', auth_token, user_id)
        self.update_setting('Accounts_RegistrationForm', 'Disabled', auth_token, user_id)
        self.update_setting('Accounts_TwoFactorAuthentication_Enabled', False, auth_token, user_id)
        self.update_setting('Show_Setup_Wizard', 'completed', auth_token, user_id)
        self.update_setting('Accounts_Send_Email_When_Activating', False, auth_token, user_id)
        self.update_setting('Accounts_Send_Email_When_Deactivating', False, auth_token, user_id)
        self.update_setting('FileUpload_Storage_Type', 'FileSystem', auth_token, user_id)

        app_storage_dir = storage.init_storage(APP_NAME, USER_NAME)

        self.update_setting('FileUpload_FileSystemPath', app_storage_dir, auth_token, user_id)

        response = requests.post("{0}/users.delete".format(self.base_url),
                                 headers={"X-Auth-Token": auth_token, "X-User-Id": user_id},
                                 json={"userId": user_id})
        result = json.loads(response.text)
        if not result['success']:
            self.log.error(response.text.encode("utf-8"))
            raise Exception('unable to delete install user')

        with open(self.install_file, 'w') as f:
            f.write('installed\n')

    def update_setting(self, name, value, auth_token, user_id):
        # throttle api requests
        time.sleep(5)
        session = requests_unixsocket.Session()
        response = session.post("{0}/settings/{1}".format(self.base_url, name),
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
