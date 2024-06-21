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
SUPPORTED_MAJOR_VERSION = '5.1'
logger.init(logging.DEBUG, console=True, line_format='%(message)s')



class Installer:
    def __init__(self):
        self.log = logger.get_logger('rocketchat')
        self.snap_dir = '/snap/rocketchat/current'
        self.data_dir = '/var/snap/rocketchat/current'
        self.common_dir = '/var/snap/rocketchat/common'
        self.app_url = urls.get_app_url(APP_NAME)
        self.database_dump = join(self.data_dir, 'database.dump.gzip')
        self.database_dir = join(self.data_dir, 'mongodb')
        self.rocketchat_env_file_source = join(self.snap_dir, 'config', 'rocketchat.env')
        self.rocketchat_env_file_target = join(self.data_dir, 'config', 'rocketchat.env')
        self.version_new_file = join(self.snap_dir, 'node', 'rocketchat.version')
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
        except CalledProcessError as e:
            self.log.error("pre_refresh error: " + e.output.decode())
            raise e

    def post_refresh(self):
        self.log.info('post refresh') 
        if not path.isfile(self.database_dump):
            raise Exception('please export database manually to {0}'.format(self.database_dump))
        self.log.info(check_output('rm -rf {0}'.format(self.database_dir), shell=True))
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
        fs.makepath(self.database_dir)

        gen.generate_file_jinja(self.rocketchat_env_file_source, self.rocketchat_env_file_target, {'url': self.app_url})

        fs.chownpath(self.data_dir, USER_NAME, recursive=True)
        fs.chownpath(self.common_dir, USER_NAME, recursive=True)

        self.prepare_storage()

    def configure(self):
        self.log.info('configure')
        wait_for_rest(requests_unixsocket.Session(), self.base_url, 200, 100)

        if path.isfile(self.version_old_file):
            self._upgrade()
        else:
            self._install()
 
    def _install(self):
        shutil.copy(self.version_new_file, self.version_old_file)
        storage.init_storage(APP_NAME, USER_NAME)

    def check_major_version(self):
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
        self.check_major_version()
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

    
    def prepare_storage(self):
        app_storage_dir = storage.init_storage(APP_NAME, USER_NAME)
        return app_storage_dir
