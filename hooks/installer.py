import json
import logging
import uuid
from os import path
from os.path import join

import requests

from syncloudlib import fs, linux, gen, logger
from syncloudlib.application import paths, urls, storage

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
        self.app_dir = paths.get_app_dir(APP_NAME)
        self.app_data_dir = paths.get_data_dir(APP_NAME)
        self.app_url = urls.get_app_url(APP_NAME)
        self.install_file = join(self.app_data_dir, 'installed')

    def install(self):
    
        linux.useradd(USER_NAME)

        fs.makepath(join(self.app_data_dir, 'log'))
        fs.makepath(join(self.app_data_dir, 'nginx'))
        fs.makepath(join(self.app_data_dir, 'mongodb'))
        mongodb_socket_file = '{0}/mongodb.sock'.format(self.app_data_dir)
        mongodb_socket_file_escaped = mongodb_socket_file.replace('/', '2%F')
        variables = {
            'app_dir': self.app_dir,
            'app_data_dir': self.app_data_dir,
            'url': self.app_url,
            'web_secret': unicode(uuid.uuid4().hex),
            'port': PORT,
            'mongodb_port': MONGODB_PORT,
            'mongodb_socket_file': mongodb_socket_file,
            'mongodb_socket_file_escaped': mongodb_socket_file_escaped
        }

        templates_path = join(self.app_dir, 'config.templates')
        config_path = join(self.app_data_dir, 'config')

        gen.generate_files(templates_path, config_path, variables)
       
        fs.chownpath(self.app_data_dir, USER_NAME, recursive=True)
        
        prepare_storage()

    def configure(self):
        if path.isfile(self.install_file):
            self.log.info('already configured')
            return
            
        password = unicode(uuid.uuid4().hex)
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
      
        response = requests.post("{0}/login" .format(REST_URL), json={"username": "installer", "password": password})
        result = json.loads(response.text)
        if not result['status'] == 'success':
            self.log.error(response.text.encode("utf-8"))
            self.log.info(result['status'])
            raise Exception('unable to login under install user')
     
        auth_token = result['data']['authToken']
        user_id = result['data']['userId']
        self.log.info('install account token extracted')
  
        self.update_setting('LDAP_Enable', True, auth_token, user_id)
        self.update_setting('LDAP_Host', 'localhost', auth_token, user_id)
        self.update_setting('LDAP_BaseDN', 'dc=syncloud,dc=org', auth_token, user_id)
        self.update_setting('LDAP_Authentication', True, auth_token, user_id)
        self.update_setting('LDAP_Authentication_UserDN', 'dc=syncloud,dc=org', auth_token, user_id)
        self.update_setting('LDAP_Authentication_Password', 'syncloud', auth_token, user_id)
        self.update_setting('LDAP_User_Search_Filter', '(objectclass=inetOrgPerson)', auth_token, user_id)
        self.update_setting('LDAP_User_Search_Field', 'cn', auth_token, user_id)
        self.update_setting('LDAP_Username_Field', 'cn', auth_token, user_id)
        self.update_setting('Accounts_RegistrationForm', 'Disabled', auth_token, user_id)
        self.update_setting('LDAP_Internal_Log_Level', 'debug', auth_token, user_id)
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
 
        response = requests.post("{0}/settings/{1}" .format(REST_URL, name),
                                 headers={"X-Auth-Token": auth_token, "X-User-Id": user_id},
                                 json={"value": value})
        result = json.loads(response.text)
        if not result['success']:
            self.log.info('cannot update setting: {0}'.format(name))
            self.log.info('response: {0}'.format(response.text.encode("utf-8")))
            raise Exception('unable to update settings')


def prepare_storage():
    app_storage_dir = storage.init_storage(APP_NAME, USER_NAME)
    return app_storage_dir
