from os.path import dirname, join, abspath, isdir
from os import listdir, environ
import sys
from subprocess import check_output
app_path = abspath(join(dirname(__file__), '..'))

lib_path = join(app_path, 'lib')
libs = [join(lib_path, item) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(lambda l: sys.path.insert(0, l), libs)
from bs4 import BeautifulSoup

from os.path import isdir, join
import requests
import time
from subprocess import check_output, CalledProcessError
import shutil
import uuid
from syncloud_app import logger
import json
from syncloud_platform.application import api
from syncloud_platform.gaplib import fs, linux, gen
from syncloudlib.application import paths, urls


APP_NAME = 'rocketchat'
USER_NAME = 'rocketchat'
SYSTEMD_ROCKETCHAT = 'rocketchat-server'
SYSTEMD_NGINX = 'rocketchat-nginx'
SYSTEMD_MONGODB = 'rocketchat-mongodb'
PORT = 3000
MONGODB_PORT = 27017
REST_URL = "http://localhost:{0}/api/v1".format(PORT)

def install():
    log = logger.get_logger('rocketchat')

    app_dir = paths.get_app_dir(APP_NAME)
    app_data_dir = paths.get_data_dir(APP_NAME)
    app_url = urls.get_app_url(APP_NAME)

    linux.useradd(USER_NAME)

    fs.makepath(join(app_data_dir, 'log'))
    fs.makepath(join(app_data_dir, 'nginx'))
    fs.makepath(join(app_data_dir, 'mongodb'))

    variables = {
        'app_dir': app_dir,
        'app_data_dir': app_data_dir,
        'url': app_url,
        'web_secret': unicode(uuid.uuid4().hex),
        'port': PORT,
        'mongodb_port': MONGODB_PORT
    }

    templates_path = join(app_dir, 'config.templates')
    config_path = join(app_data_dir, 'config')

    gen.generate_files(templates_path, config_path, variables)

    fs.chownpath(app_data_dir, USER_NAME, recursive=True)
    
    if 'SNAP' not in environ:
        app = api.get_app_setup(APP_NAME)
    
        fs.chownpath(app_dir, USER_NAME, recursive=True)
  
        app.add_service(SYSTEMD_MONGODB)
        app.add_service(SYSTEMD_ROCKETCHAT)
        app.add_service(SYSTEMD_NGINX)

def after_service_start():
    log = logger.get_logger('rocketchat')

    password = unicode(uuid.uuid4().hex)
    response = requests.post("{0}/users.register".format(REST_URL), json={ "username": "installer", "email": "installer@example.com", "pass": password, "name": "installer" } )
    result = json.loads(response.text)
    if not result['success']:
        log.info('cannot create install account')
        log.info('response: {0}'.format(response.text.encode("utf-8")))
        return
        
    log.info('install account has been created')
      
    response = requests.post("{0}/login" .format(REST_URL), json={ "username": "installer", "password": password } )
    result = json.loads(response.text)
    if not result['status'] == 'success':
        log.error(response.text.encode("utf-8"))
        log.info(result['status'])
        raise Exception('unable to login under install user')
    
    authToken = result['data']['authToken']
    userId = result['data']['userId']
    log.info('install account token extracted')
  
    update_setting('LDAP_Enable', True, authToken, userId)
    update_setting('LDAP_Host', 'localhost', authToken, userId)
    update_setting('LDAP_BaseDN', 'dc=syncloud,dc=org', authToken, userId)
    update_setting('LDAP_Authentication', True, authToken, userId)
    update_setting('LDAP_Authentication_UserDN', 'dc=syncloud,dc=org', authToken, userId)
    update_setting('LDAP_Authentication_Password', 'syncloud', authToken, userId)
    update_setting('LDAP_User_Search_Filter', '(objectclass=inetOrgPerson)', authToken, userId)
    update_setting('LDAP_User_Search_Field', 'cn', authToken, userId)
    update_setting('LDAP_Username_Field', 'cn', authToken, userId)
    update_setting('Accounts_RegistrationForm', 'Public', authToken, userId)
    update_setting('LDAP_Internal_Log_Level', 'debug', authToken, userId)


def update_setting(name, value, authToken, userId):
      
    response = requests.post("{0}/settings/{1}" .format(REST_URL, name), headers={"X-Auth-Token": authToken, "X-User-Id": userId}, json={"value": value} )
    result = json.loads(response.text)
    if not result['success']:
        log.info('cannot update setting: {0}'.format(name))
        log.info('response: {0}'.format(response.text.encode("utf-8")))
        raise Exception('unable to update settings')


        
def remove():
    app = api.get_app_setup(APP_NAME)

    app.remove_service(SYSTEMD_NGINX)
    app.remove_service(SYSTEMD_ROCKETCHAT)
    app.remove_service(SYSTEMD_MONGODB)

    app_dir = paths.get_data_dir(APP_NAME)

    fs.removepath(app_dir)

