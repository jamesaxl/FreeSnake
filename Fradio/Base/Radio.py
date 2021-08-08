"""
FCP API in Python created by James Axl 2018

For FCP documentation, see https://wiki.freenetproject.org/FCPv2 still under construction
"""

try:
    from Fcp.Node import Node
except ModuleNotFoundError:
    raise ModuleNotFoundError('Fcp module is required')

try:
    import magic
except ModuleNotFoundError:
    raise ModuleNotFoundError('magic module is required')

import os
import shutil
from pathlib import Path
from time import sleep

from .Core import Core
from .DataBase import RadioModel, TrackModel, init_db_con
from .Logger import LOGGER
from .Track import Track

SUPPORTED_AUDIO_FORMAT = ['audio/ogg', 'audio/mpeg']


class Radio(object):
    def __init__(self):
        self.core = Core()
        self.core.connect_to_node()
        self.db_con = init_db_con()
        self.radio_model = RadioModel(self.db_con)
        self.track_model = TrackModel(self.db_con)
        self.update_flag = False
        self.temp_path = None

        self.name = None
        self.path_dir = None
        self.identifier = None
        self.version = 0
        self.description = None
        self.files_to_upload = None
        self.pub = None
        self.prv = None
        self.track = None

    def insert(self,
               name,
               path_dir,
               description=''):

        resume = False
        is_exist = self.radio_model.check_if_radio_exist(name)

        if is_exist:
            LOGGER.info('RADIO {0} ALREADY EXIST. CHECK IF IT IS UPLOADED'.format(name))
            sleep(2)
            if self.radio_model.check_if_radio_uploaded(name):
                LOGGER.info('RADIO {0} ALREADY IS UPLOADED'.format(name))
                return
            else:
                resume = True
                LOGGER.info('RESUME THE UPLOAD OF RADIO {0}'.format(name))

        self.name = name
        self.path_dir = path_dir
        self.identifier = self.core.get_a_uuid()
        self.version = 0
        self.description = description

        if not Path(self.path_dir).exists():
            raise FileNotFoundError('{0} does not exist'.format(self.path_dir))

        for _file in list(Path(self.path_dir).glob('*')):
            if Path(_file).is_dir():
                raise Exception('{0} is a sub-folder'.format(_file))

            if not magic.from_file(_file.as_posix(), mime=True) in SUPPORTED_AUDIO_FORMAT:
                raise Exception('{0} is not ogg file'.format(_file))

        # This folder contains file that changed and will be uploaded
        Path('/tmp/{0}'.format(self.identifier)).mkdir(parents=True, exist_ok=True)

        self.temp_path = '/tmp/{0}'.format(self.identifier)
        for _file in list(Path(self.path_dir).glob('*')):
            shutil.copy(_file, self.temp_path)

        self.files_to_upload = self.sort_files_by_size()

        if not resume:
            self.pub, self.prv = self.core.node.node_request.generate_keys(name='{0}'.format(self.name))

            self.radio_model.insert(self.identifier,
                                    self.name,
                                    self.path_dir,
                                    self.prv,
                                    self.pub,
                                    self.version)
        else:
            self.pub = is_exist[6]
            self.prv = is_exist[5]
            self.identifier = is_exist[0]

        self.track = Track(self.files_to_upload, self)
        self.track.node_request = self.core.node.node_request
        self.track.make_track()

        self.track.generate_chk_before_upload(self.generate_chk_before_upload_callback)

    def get_radio(self, pub, path_dir, file_name):
        if not Path(path_dir).exists():
            raise FileNotFoundError('{0} does not exist'.format(path_dir))

        f_stream = open('{0}/{1}'.format(path_dir, file_name), 'ab')
        self.core.node.node_request.get_stream(uri=pub,
                                               global_queue=True,
                                               stream=f_stream,
                                               callback=self.get_radio_callback)

    def update(self, name,
               path_dir,
               description=''):

        radio = self.radio_model.check_if_radio_uploaded(name)
        if not radio:
            LOGGER.info('WEBSITE {0} DOES NOT EXIST.'.format(name))
        else:
            self.version = radio[8] + 1
            self.prv = radio[4]
            self.pub = radio[5]

            self.name = name
            self.path_dir = path_dir
            self.identifier = radio[0]
            check_path_dir = Path(self.path_dir)

            if not check_path_dir.exists():
                raise FileNotFoundError('{0} does not exist'.format(self.path_dir))

            for _file in list(Path(self.path_dir).glob('*')):
                if Path(_file).is_dir():
                    raise Exception('{0} is a sub-folder'.format(_file))

                if not magic.from_file(_file.as_posix(), mime=True) in SUPPORTED_AUDIO_FORMAT:
                    raise Exception('{0} is not ogg file'.format(_file))

            # This folder contains file that changed and will be uploaded
            Path('/tmp/{0}'.format(self.identifier)).mkdir(parents=True, exist_ok=True)

            self.temp_path = '/tmp/{0}'.format(self.identifier)
            for _file in list(Path(self.path_dir).glob('*')):
                shutil.copy(_file, self.temp_path)

            self.files_to_upload = self.sort_files_by_size()

            self.radio_model.update(self.path_dir,
                                    self.prv,
                                    self.pub,
                                    self.version,
                                    self.name)

            self.track = Track(self.files_to_upload, self)
            self.track.node_request = self.core.node.node_request
            self.track.make_track()

            self.track.generate_chk_before_upload(self.generate_chk_before_upload_callback)
            self.update_flag = True

    def delete(self, name):
        self.radio_model.delete(name)

    def select_radio(self, name):
        radio = self.radio_model.check_if_radio_exist(name)
        return radio

    def select_all(self, page=1):
        radios = self.radio_model.select_all(page)
        return radios

    def sort_files_by_size(self):
        files = []

        for _file in list(Path(self.temp_path).glob('*')):
            metadata_content_type = magic.from_file(_file.as_posix(), mime=True)
            files.append({'name': _file.name,
                          'size': os.stat(_file.as_posix()).st_size,
                          'path': _file.as_posix(),
                          'metadata_content_type': metadata_content_type,
                          })

        return sorted(files, key=lambda k: k['size'])

    def upload_radio(self, upload_radio_callback):
        self.core.node.node_request.put_file(uri='{0}-{1}'.format(self.prv, self.version),
                                             identifier=self.identifier,
                                             global_queue=True,
                                             file_path='{0}/{1}.txt'.format(self.temp_path, self.name),
                                             callback=upload_radio_callback)

    def upload_radio_callback(self, event, result):
        if event == 'URIGenerated':
            LOGGER.info('URL: {0} IS GENERATED FOR RADIO: {1}'.format(result['URI'], self.name))
        elif event == 'SimpleProgress':
            succeeded = int(result['Succeeded'])
            required = int(result['Required'])
            progress = (succeeded / required) * 100.0
            LOGGER.info('RADIO: {0} PROGRESS: {1}%'.format(self.name, round(progress, 2)))
        elif event == 'PutSuccessful':
            self.radio_model.update_upload(self.identifier)

            if self.update_flag:
                self.sync_db_with_dir(result['Identifier'])
                self.update_flag = False

            self.track.queue = {'number_of_files': 0, 'data': []}

            LOGGER.info('RADIO: {0} PROGRESS: 100%'.format(self.name))
            LOGGER.info('RADIO: {0} IS UPLOADED WITH URI: {1}'.format(self.name, result['URI']))
            shutil.rmtree('/tmp/{0}'.format(self.identifier))

        elif event == 'PutFailed':
            LOGGER.info('ManifestFileUpload PutFailed Code : {0}, Description : {1} '.format(result['Code'],
                                                                                             result['CodeDescription']))
            if result.get('ExtraDescription', False):
                LOGGER.info('ManifestFileUpload PutFailed Code : {0}, ExtraDescription : {1} '.format(result['Code'],
                                                                                                      result[
                                                                                                          'ExtraDescription']))

    def upload_track_callback(self, event, result):
        if event == 'URIGenerated':
            if not self.track_model.check_if_chk_exist(result['URI'], self.identifier):
                self.track_model.insert(self.track.temp['name'],
                                        self.track.temp['metadata_content_type'],
                                        os.stat(self.track.temp['path']).st_size,
                                        result['URI'],
                                        self.identifier)

            self.track.temp['chk'] = result['URI']
            LOGGER.info('URL: {0} IS GENERATED FOR FILE: {1}'.format(result['URI'], self.track.temp['name']))

        elif event == 'SimpleProgress':
            succeeded = int(result['Succeeded'])
            required = int(result['Required'])
            progress = (succeeded / required) * 100.0
            LOGGER.info('FILE: {0} PROGRESS: {1}%'.format(self.track.temp['name'], round(progress, 2)))

        elif event == 'PutSuccessful':
            self.track_model.update_upload(result['URI'])
            LOGGER.info('FILE: {0} PROGRESS: 100%'.format(self.track.temp['name']))
            LOGGER.info('FILE: {0} IS UPLOADED WITH URL: {1}'.format(self.track.temp['name'], result['URI']))

        elif event == 'PersistentRequestRemoved':
            sleep(1)
            self.track.temp = {}
            self.track.upload_track(self.upload_track_callback)

        elif event == 'PutFailed':
            LOGGER.info('SeparateFileUpload PutFailed Code : {0}, Description : {1} '.format(result['Code'],
                                                                                             result['CodeDescription']))
            if result.get('ExtraDescription', False):
                LOGGER.info('SeparateFileUpload PutFailed Code : {0}, ExtraDescription : {1} '.format(result['Code'],
                                                                                                      result[
                                                                                                          'ExtraDescription']))

    def get_radio_callback(self, event, result):
        LOGGER.info(event)

    def generate_radio_file(self, chk):
        f = open('{0}/{1}.txt'.format(self.temp_path, self.name), 'a+')
        f.write('{0}\n'.format(chk))
        f.close()

    def generate_chk_before_upload_callback(self, event, result):
        if event == 'PutSuccessful':
            self.generate_radio_file(result['URI'])
            sleep(1)
            self.track.generate_chk_before_upload(self.generate_chk_before_upload_callback)

        elif event == 'PutFailed':
            LOGGER.info('Generate-CHK PutFailed Code : {0}, Description : {1} '.format(result['Code'],
                                                                                       result['CodeDescription']))
            if result.get('ExtraDescription', False):
                LOGGER.info('Generate-CHK PutFailed Code : {0}, ExtraDescription : {1} '.format(result['Code'], result[
                    'ExtraDescription']))

    def sync_db_with_dir(self, identifier):
        # sync between dir and database
        LOGGER.info('SYNC DIR AND DATABASE')

        track_files_in_db = self.track_model.select_belong_to_radio(identifier)
        track_files_in_db = [_file[1] for _file in track_files_in_db]
        track_files_in_dir = [_file['name'] for _file in self.track.queue['data'] if _file['name'] is not None]
        track_files_to_delete_from_db = [_file for _file in track_files_in_db if not _file in track_files_in_dir]

        for _file in track_files_to_delete_from_db:
            self.track_model.delete(_file, identifier)
