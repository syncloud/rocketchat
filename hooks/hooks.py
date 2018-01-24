import sys
from os import listdir, environ, path
from os.path import dirname, join, abspath, isdir

app_path = abspath(join(dirname(__file__), '..'))

lib_path = join(app_path, 'lib')
libs = [join(lib_path, item) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(lambda l: sys.path.insert(0, l), libs)

from os.path import join
import requests
import uuid
from syncloud_app import logger
import json
from syncloud_platform.application import api
from syncloud_platform.gaplib import fs, linux, gen
from syncloudlib.application import paths, urls, storage


APP_NAME = 'rocketchat'
USER_NAME = 'rocketchat'
SYSTEMD_ROCKETCHAT = 'rocketchat-server'
SYSTEMD_NGINX = 'rocketchat-nginx'
SYSTEMD_MONGODB = 'rocketchat-mongodb'
PORT = 3000
MONGODB_PORT = 27017
REST_URL = "http://localhost:{0}/api/v1".format(PORT)


class RocketChatInstaller():
    def __init__(self):
        self.log = logger.get_logger('rocketchat')
        self.app_dir = paths.get_app_dir(APP_NAME)
        self.app_data_dir = paths.get_data_dir(APP_NAME)
        self.app_url = urls.get_app_url(APP_NAME)
        #self.app = api.get_app_setup(APP_NAME)
        self.install_file = join(self.app_data_dir, 'installed')

    
    def install(self):
    
        linux.useradd(USER_NAME)

        fs.makepath(join(self.app_data_dir, 'log'))
        fs.makepath(join(self.app_data_dir, 'nginx'))
        fs.makepath(join(self.app_data_dir, 'mongodb'))

        variables = {
            'app_dir': self.app_dir,
            'app_data_dir': self.app_data_dir,
            'url': self.app_url,
            'web_secret': unicode(uuid.uuid4().hex),
            'port': PORT,
            'mongodb_port': MONGODB_PORT
        }

        templates_path = join(self.app_dir, 'config.templates')
        config_path = join(self.app_data_dir, 'config')

        gen.generate_files(templates_path, config_path, variables)
       
        fs.chownpath(self.app_data_dir, USER_NAME, recursive=True)
        
        self.prepare_storage()
        
        if 'SNAP' not in environ:
            app = api.get_app_setup(APP_NAME)
    
            fs.chownpath(self.app_dir, USER_NAME, recursive=True)
  
            app.add_service(SYSTEMD_MONGODB)
            app.add_service(SYSTEMD_ROCKETCHAT)
            app.add_service(SYSTEMD_NGINX)


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
     
        authToken = result['data']['authToken']
        userId = result['data']['userId']
        self.log.info('install account token extracted')
  
        self.update_setting('LDAP_Enable', True, authToken, userId)
        self.update_setting('LDAP_Host', 'localhost', authToken, userId)
        self.update_setting('LDAP_BaseDN', 'dc=syncloud,dc=org', authToken, userId)
        self.update_setting('LDAP_Authentication', True, authToken, userId)
        self.update_setting('LDAP_Authentication_UserDN', 'dc=syncloud,dc=org', authToken, userId)
        self.update_setting('LDAP_Authentication_Password', 'syncloud', authToken, userId)
        self.update_setting('LDAP_User_Search_Filter', '(objectclass=inetOrgPerson)', authToken, userId)
        self.update_setting('LDAP_User_Search_Field', 'cn', authToken, userId)
        self.update_setting('LDAP_Username_Field', 'cn', authToken, userId)
        self.update_setting('Accounts_RegistrationForm', 'Public', authToken, userId)
        self.update_setting('LDAP_Internal_Log_Level', 'debug', authToken, userId)
        self.update_setting('FileUpload_Storage_Type', 'FileSystem', authToken, userId)
        
        app_storage_dir = storage.init_storage(APP_NAME, USER_NAME)
        
        self.update_setting('FileUpload_FileSystemPath', app_storage_dir, authToken, userId)
        
        response = requests.post("{0}/users.delete".format(REST_URL), headers={"X-Auth-Token": authToken, "X-User-Id": userId}, json={"userId": userId})
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

    def prepare_storage(self):
        app_storage_dir = storage.init_storage(APP_NAME, USER_NAME)
        return app_storage_dir
        
    def remove(self):
        app = api.get_app_setup(APP_NAME)

        app.remove_service(SYSTEMD_NGINX)
        app.remove_service(SYSTEMD_ROCKETCHAT)
        app.remove_service(SYSTEMD_MONGODB)

        fs.removepath(self.app_dir)
