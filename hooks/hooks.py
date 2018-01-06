from os.path import dirname, join, abspath, isdir
from os import listdir, environ
import sys

app_path = abspath(join(dirname(__file__), '..'))

lib_path = join(app_path, 'lib')
libs = [join(lib_path, item) for item in listdir(lib_path) if isdir(join(lib_path, item))]
map(lambda l: sys.path.insert(0, l), libs)
from bs4 import BeautifulSoup

from os.path import isdir, join
import requests_unixsocket
import time
from subprocess import check_output
import shutil
import uuid
from syncloud_app import logger

from syncloud_platform.application import api
from syncloud_platform.gaplib import fs, linux, gen
from syncloudlib.application import paths
APP_NAME = 'rocketchat'
USER_NAME = 'rocketchat'
SYSTEMD_ROCKETCHAT = 'rocketchat-server'
SYSTEMD_NGINX = 'rocketchat-nginx'
SYSTEMD_MONGODB = 'rocketchat-mongodb'
PORT = 3000


def install():
    log = logger.get_logger('rocketchat_installer')

    app = api.get_app_setup(APP_NAME)
    app_dir = paths.get_app_dir(APP_NAME)
    app_data_dir = paths.get_data_dir(APP_NAME)

    linux.useradd(USER_NAME)

    fs.makepath(join(app_data_dir, 'log'))
    fs.makepath(join(app_data_dir, 'nginx'))
    fs.makepath(join(app_data_dir, 'mongodb'))

    variables = {
        'app_dir': app_dir,
        'app_data_dir': app_data_dir,
        'url': app.app_url(),
        'web_secret': unicode(uuid.uuid4().hex),
        'port': PORT
    }

    templates_path = join(app_dir, 'config.templates')
    config_path = join(app_data_dir, 'config')

    gen.generate_files(templates_path, config_path, variables)

    fs.chownpath(app_data_dir, USER_NAME, recursive=True)
    
    if 'SNAP' not in environ:
        fs.chownpath(app_dir, USER_NAME, recursive=True)
  
        app.add_service(SYSTEMD_MONGODB)
        app.add_service(SYSTEMD_ROCKETCHAT)
        app.add_service(SYSTEMD_NGINX)
    

def remove():
    app = api.get_app_setup(APP_NAME)

    app.remove_service(SYSTEMD_NGINX)
    app.remove_service(SYSTEMD_ROCKETCHAT)
    app.remove_service(SYSTEMD_MONGODB)

    app_dir = app.get_install_dir()

    fs.removepath(app_dir)

