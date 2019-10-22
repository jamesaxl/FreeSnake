# -*- coding: utf-8 -*-

'''
FCP API in Python created by James Axl 2018

For FCP documentation, see http://wiki.freenetproject.org/FCPv2 still under construction
'''

from .Logger import LOGGER
from .DataBase import SeparateModel
from .DataBase import ManifestModel


# ad hoq - my node sometimes dies at 500 simultaneous uploads. 
#This is half the space in the estimated size of the manifest.
DEFAULT_MAX_NUMBER_SEPARATE_FILES = 512

class Separate(object):
    '''
    
    '''
    def __init__(self, files_to_upload, website):
        self.files_to_upload = files_to_upload
        self.queue = { 'data' : [], 'number_of_files' : 0 }
        self.files_to_generate = []
        self.node_request = None
        self.website = website

    def make_separate(self):
        for _file in self.files_to_upload:
            if ( self.queue['number_of_files'] < DEFAULT_MAX_NUMBER_SEPARATE_FILES ):
                self.queue['data'].append({
                                            'name' : _file['name'], 
                                            'size' : _file['size'], 
                                            'path' : _file['path'], 
                                            'metadata_content_type' : _file['metadata_content_type'],
                                           })
                self.queue['number_of_files'] += 1

        for _file in self.queue['data']:
            self.files_to_generate.append(_file)

        LOGGER.info('MAKE SEPARATE QUEUE')

    def upload_separate(self, callback_func):
        if not self.queue['data']:
            self.website.manifest.upload_manifest(self.website.upload_manifest_callback) # from WebSite
        else:
            self.temp = self.queue['data'].pop()
            self.node_request.put_file(uri = 'CHK@', 
                                   global_queue = True, 
                                   file_path = self.temp['path'], 
                                   callback = callback_func)

    def generate_chk_before_upload(self, callback_func):
        if not self.files_to_generate:
            self.upload_separate(self.website.upload_separate_callback) # from WebSite
        else:
            ready = self.files_to_generate.pop()
            self.node_request.put_file(uri = 'CHK@', 
                                   global_queue = True, 
                                   file_path = ready['path'],
                                   get_chk_only = True, 
                                   callback = callback_func)
