# -*- coding: utf-8 -*-

'''
FCP API in Python created by James Axl 2018

For FCP documentation, see http://wiki.freenetproject.org/FCPv2 still under construction
'''

from .Logger import LOGGER

## 2.0 MiB: As used by the freenet default dir inserter. 
#Reduced by 512 bytes per redirect. TODO: Add a larger side-container 
#for additional medium-size files like images. Doing this here, 
#because here we know what is linked in the index file.
DEFAULT_MAX_MANIFEST_SIZE_BYTES = 1024 * 1024 * 2

class Manifest(object):
    '''
    
    '''
    def __init__(self, files_to_upload, default_index):
        self.files_to_upload = files_to_upload
        self.default_index = default_index
        self.queue = { 'data' : [], 'size' : 0 }
        self.node_request = None
        self.prv = None
        self.identifier = None
        self.name_of_site = None
        self.path_dir = None
        
    def make_manifest(self):
        index_file = next(_file for _file in self.files_to_upload if _file['name'] == self.default_index)
        self.queue['data'].append({ 'name' : index_file['name'], 
                                    'size' : index_file['size'], 
                                    'path' : index_file['path'], 
                                    'metadata_content_type' : index_file['metadata_content_type'],
                                   })

        self.files_to_upload.remove(index_file)
        for _file in self.files_to_upload:
            if _file['metadata_content_type'] == 'text/html':
                if (self.queue['size'] + _file['size']) < DEFAULT_MAX_MANIFEST_SIZE_BYTES:
                    self.queue['data'].append({ 
                                                'name' : _file['name'], 
                                                'size' : _file['size'], 
                                                'path' : _file['path'], 
                                                'metadata_content_type' : _file['metadata_content_type'],
                                               })
                    self.queue['size'] += _file['size']

        for _file in self.files_to_upload:
            if _file['metadata_content_type'] != 'text/html':
                if (self.queue['size'] + _file['size']) < DEFAULT_MAX_MANIFEST_SIZE_BYTES:
                    self.queue['data'].append({
                                                'name' : _file['name'], 
                                                'size' : _file['size'], 
                                                'path' : _file['path'], 
                                                'metadata_content_type' : _file['metadata_content_type'],
                                               })

                    self.queue['size'] += _file['size']
                    
        # update self.files_to_upload
        self.files_to_upload = [_file for _file in self.files_to_upload if _file not in self.queue['data']]
        LOGGER.info('MAKE MANIFEST QUEUE')

    def upload_manifest(self, callback_func):
        if self.queue['data']:
            self.node_request.put_complex_directory_files(uri = self.prv,
                                                               identifier = self.identifier,
                                                               global_queue = True, 
                                                               site_name = self.name_of_site, 
                                                               default_name = self.default_index, 
                                                               directory = self.path_dir,
                                                               manifest_files = self.queue['data'],
                                                               callback = callback_func)

