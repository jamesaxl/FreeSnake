# -*- coding: utf-8 -*-

'''
FCP API in Python created by James Axl 2018

For FCP documentation, see http://wiki.freenetproject.org/FCPv2 still under construction
'''

try:
    from Fcp.Node import Node
except ModuleNotFoundError:
    raise ModuleNotFoundError('Fcp module is required')

try:
    import magic
except ModuleNotFoundError:
    raise ModuleNotFoundError('magic module is required')
    
import shutil
import fileinput
import sys, os
from time import sleep
from pathlib import Path
from .Core import Core
from .Logger import LOGGER
from .DataBase import WebsiteModel, ManifestModel, SeparateModel, init_db_con
from .Manifest import Manifest
from .Separate import Separate

class WebSite(object):
    '''
    
    '''
    def __init__(self):
        self.core = Core()
        self.core.connect_to_node()
        self.db_con = init_db_con()
        self.website_model = WebsiteModel(self.db_con)
        self.manifest_model = ManifestModel(self.db_con)
        self.separate_model = SeparateModel(self.db_con)
        self.update_flag = False

    def insert(self, name_of_site, 
                     path_dir,
                     default_index):

        resume = False
        is_exist = self.website_model.check_if_website_exist(name_of_site)
        if is_exist:
            LOGGER.info('WEBSITE {0} ALREADY EXIST. CHECK IF WEBSITE IS UPLOADED'.format(name_of_site))
            sleep(2)
            if self.website_model.check_if_website_uploaded(name_of_site):
                LOGGER.info('WEBSITE {0} ALREADY IS UPLOADED'.format(name_of_site))
                return
            else:
                resume = True
                LOGGER.info('RESUME THE UPLOAD OF WEBSITE {0}'.format(name_of_site))

        self.name_of_site = name_of_site
        self.path_dir = path_dir
        self.default_index = default_index
        self.identifier = self.core.get_a_uuid()
        self.version = 0
        
        if not Path(self.path_dir).exists():
            raise FileNotFoundError('{0} does not exist'.format(self.path_dir))

        if not Path('{0}/{1}'.format(self.path_dir, self.default_index)).exists():
            raise FileNotFoundError('{0} is not found in {1}'.format(self.default_index, self.path_dir))

        for _file in list(Path(self.path_dir).glob('*')):
            if Path(_file).is_dir():
                raise Exception('{0} is a sub-folder'.format(_file))

        # This folder contains file that changed and will be uploaded
        Path('/tmp/{0}'.format(self.identifier)).mkdir(parents=True, exist_ok=True)
        
        self.temp_path = '/tmp/{0}'.format(self.identifier)
        for _file in list(Path(self.path_dir).glob('*')):
            shutil.copy(_file, self.temp_path)

        self.files_to_upload = self.sort_files_by_size()
        
        if not resume:
            self.pub, self.prv = self.core.node.node_request.generate_keys(name='{0}'.format(self.name_of_site))

            # insert to website table
            self.website_model.insert( self.identifier, 
                                       self.name_of_site,
                                       self.default_index, 
                                       self.path_dir,
                                       self.prv, 
                                       self.pub, 
                                       self.version )
        else:
            # get from website table
            self.pub = is_exist[6]
            self.prv = is_exist[5]
            self.identifier = is_exist[0]

        self.manifest = Manifest(self.files_to_upload, self.default_index, self.version)
        self.manifest.node_request = self.core.node.node_request
        self.manifest.prv = self.prv
        self.manifest.identifier = self.identifier
        self.manifest.name_of_site = self.name_of_site
        self.manifest.path_dir = self.path_dir
        self.manifest.make_manifest()

        self.separate = Separate(self.manifest.files_to_upload, self)
        self.separate.node_request = self.core.node.node_request
        self.separate.make_separate()

        self.separate.generate_chk_before_upload(self.generate_chk_before_upload_callback)

    def update(self, name_of_site, 
                     path_dir,
                     default_index):

        web_site = self.website_model.check_if_website_uploaded(name_of_site)
        if not web_site:
            LOGGER.info('WEBSITE {0} DOES NOT EXIST.'.format(name_of_site))
        else:
            self.version = web_site[9] + 1
            self.prv =  web_site[5]
            self.pub = web_site[6]
            
            self.name_of_site = name_of_site
            self.path_dir = path_dir
            self.default_index = default_index
            self.identifier = web_site[0]
            check_path_dir = Path(self.path_dir)
        
            if not check_path_dir.exists():
                raise FileNotFoundError('{0} does not exist'.format(self.path_dir))

            if not Path('{0}/{1}'.format(self.path_dir, self.default_index)).exists():
                raise FileNotFoundError('{0} is not found in {1}'.format(self.default_index, self.path_dir))

            for _file in list(Path(self.path_dir).glob('*')):
                if Path(_file).is_dir():
                    raise Exception('{0} is a sub-folder'.format(_file))

            # This folder contains file that changed and will be uploaded
            Path('/tmp/{0}'.format(self.identifier)).mkdir(parents=True, exist_ok=True)
        
            self.temp_path = '/tmp/{0}'.format(self.identifier)
            for _file in list(Path(self.path_dir).glob('*')):
                shutil.copy(_file, self.temp_path)
            
            self.files_to_upload = self.sort_files_by_size()

            self.website_model.update(self.path_dir, 
                                    self.prv, 
                                    self.pub, 
                                    self.version, 
                                    self.default_index, 
                                    self.name_of_site)

            self.manifest = Manifest(self.files_to_upload, self.default_index, self.version)
            self.manifest.node_request = self.core.node.node_request
            self.manifest.prv = self.prv
            self.manifest.identifier = self.identifier
            self.manifest.name_of_site = self.name_of_site
            self.manifest.path_dir = self.path_dir
            self.manifest.make_manifest()

            self.separate = Separate(self.manifest.files_to_upload, self)
            self.separate.node_request = self.core.node.node_request
            self.separate.make_separate()

            self.separate.generate_chk_before_upload(self.generate_chk_before_upload_callback)
            self.update_flag = True

    def delete(self, name_of_site):
        website_model.delete(name_of_site)

    def select_website(self, name_of_site):
        website = self.website_model.check_if_website_exist(name_of_site)
        return website

    def select_all(self, page = 1):
        websites = self.website_model.select_all(page)
        return websites

    def sort_files_by_size(self):
        files = []
        for _file in list(Path(self.temp_path).glob('*')):
            metadata_content_type = magic.from_file(_file.as_posix(), mime=True)
            files.append({ 'name' : _file.name, 
                           'size' : os.stat(_file.as_posix()).st_size, 
                           'path' : _file.as_posix(), 
                           'metadata_content_type' : metadata_content_type,
                         })

        return sorted(files, key=lambda k: k['size'])

    def upload_manifest_callback(self, event, result):        
        if event == 'URIGenerated':
            for _file in self.manifest.queue['data']:
                if not self.manifest_model.check_if_manifest_exist(self.prv, _file['name'], self.identifier):
                    self.manifest_model.insert( _file['name'],
                                                _file['metadata_content_type'], 
                                                os.stat(_file['path']).st_size,
                                                self.prv,
                                                self.pub,
                                                self.identifier,
                                                self.version )
                else:
                    self.manifest_model.update(self.prv, self.version, _file['name'], os.stat(_file['path']).st_size)

            LOGGER.info('URL: {0} IS GENERATED FOR WEBSITE: {1}'.format(result['URI'], self.name_of_site))
        elif event == 'SimpleProgress':
            succeeded = int(result['Succeeded'])
            required = int(result['Required'])
            progress = (succeeded / required ) * 100.0
            LOGGER.info('WEBSITE: {0} PROGRESS: {1}%'.format(self.name_of_site, round(progress, 2)))
        elif event == 'PutSuccessful':
            for _file in self.manifest.queue['data']:
                self.manifest_model.update_upload('{0}/{1}'.format(result['URI'], _file['name']))

            self.website_model.update_upload(self.identifier)
            
            if self.update_flag:
                self.sync_db_with_dir(result['Identifier'])
                self.update_flag = False

            self.manifest.queue = { 'size' : 0, 'data' : [] }
            self.separate.queue = { 'number_of_files' : 0, 'data' : [] }

            LOGGER.info('WEBSITE: {0} PROGRESS: 100%'.format(self.name_of_site))
            LOGGER.info('WEBSITE: {0} IS UPLOADED WITH URI: {1}'.format(self.name_of_site, result['URI']))
            shutil.rmtree('/tmp/{0}'.format(self.identifier))

        elif event == 'PutFailed':
            LOGGER.info('ManifestFileUpload PutFailed Code : {0}, Description : {1} '.format( result['Code'], result['CodeDescription']) )
            if result.get('ExtraDescription', False):
                LOGGER.info('ManifestFileUpload PutFailed Code : {0}, ExtraDescription : {1} '.format( result['Code'], result['ExtraDescription']) )

    def upload_separate_callback(self, event, result):
        if event == 'URIGenerated':
            if not self.separate_model.check_if_chk_exist(result['URI'], self.identifier):
                self.separate_model.insert(self.separate.temp['name'], 
                                      self.separate.temp['metadata_content_type'], 
                                      os.stat(self.separate.temp['path']).st_size,
                                      result['URI'], 
                                      self.identifier)

            self.separate.temp['chk'] = result['URI']
            LOGGER.info('URL: {0} IS GENERATED FOR FILE: {1}'.format( result['URI'], self.separate.temp['name']) )

        elif event == 'SimpleProgress':
            succeeded = int(result['Succeeded'])
            required = int(result['Required'])
            progress = (succeeded / required ) * 100.0
            LOGGER.info('FILE: {0} PROGRESS: {1}%'.format( self.separate.temp['name'], round(progress, 2)) )

        elif event == 'PutSuccessful':
            self.separate_model.update_upload(result['URI'])
            LOGGER.info('FILE: {0} PROGRESS: 100%'.format(self.separate.temp['name']))
            LOGGER.info('FILE: {0} IS UPLOADED WITH URL: {1}'.format( self.separate.temp['name'], result['URI']) )

        elif event == 'PersistentRequestRemoved':
            sleep(1)
            self.separate.temp = {}
            self.separate.upload_separate(self.upload_separate_callback)
        
        elif event == 'PutFailed':
            LOGGER.info('SeparateFileUpload PutFailed Code : {0}, Description : {1} '.format( result['Code'], result['CodeDescription']) )
            if result.get('ExtraDescription', False):
                LOGGER.info('SeparateFileUpload PutFailed Code : {0}, ExtraDescription : {1} '.format( result['Code'], result['ExtraDescription']) )

    def update_html_file(self, _file, old_link, new_link):
        for line in fileinput.FileInput(_file, inplace = True):
            print(line.replace('href="{0}"'.format(old_link), 'href="{0}"'.format(new_link)), end='')
        
        for line in fileinput.FileInput(_file, inplace = True):
            print(line.replace('src="{0}"'.format(old_link), 'src="{0}"'.format(new_link)), end='')

    def generate_chk_before_upload_callback(self, event, result):
        if event == 'PutSuccessful':
            for _file in self.manifest.queue['data']:
                if _file['metadata_content_type'] == 'text/html':
                    self.update_html_file(_file['path'], result['URI'].split('/')[1], result['URI'])

            for _file in self.separate.queue['data']:
                if _file['metadata_content_type'] == 'text/html':
                    self.update_html_file(_file['path'], result['URI'].split('/')[1], result['URI'])

            sleep(1)
            self.separate.generate_chk_before_upload(self.generate_chk_before_upload_callback)

        elif event == 'PutFailed':
            LOGGER.info('Generate-CHK PutFailed Code : {0}, Description : {1} '.format( result['Code'], result['CodeDescription']) )
            if result.get('ExtraDescription', False):
                LOGGER.info('Generate-CHK PutFailed Code : {0}, ExtraDescription : {1} '.format( result['Code'], result['ExtraDescription']) )

    def sync_db_with_dir(self, identifier):
        # sync between dir and database
        LOGGER.info('SYNC DIR AND DATABASE')
        
        manifest_files_in_db = self.manifest_model.select_belong_to_website(identifier)
        manifest_files_in_db = [_file[1] for _file in manifest_files_in_db]
        manifest_files_in_dir = [_file['name'] for _file in self.manifest.queue['data'] if _file['name'] is not None]
        manifest_files_to_delete_from_db = [_file for _file in manifest_files_in_db if not _file in manifest_files_in_dir ]

        for _file in manifest_files_to_delete_from_db:
            self.manifest_model.delete(_file, identifier)

        separate_files_in_db = self.separate_model.select_belong_to_website(identifier)
        separate_files_in_db = [_file[1] for _file in separate_files_in_db]
        separate_files_in_dir = [_file['name'] for _file in self.separate.queue['data'] if _file['name'] is not None]
        separate_files_to_delete_from_db = [_file for _file in separate_files_in_db if not _file in separate_files_in_dir ]

        for _file in separate_files_to_delete_from_db:
            self.separate_model.delete(_file, identifier)

