"""
FCP API in Python created by James Axl 2018

For FCP documentation, see https://wiki.freenetproject.org/FCPv2 still under construction
"""

from .Logger import LOGGER

# ad hoq - my node sometimes dies at 500 simultaneous uploads.
# This is half the space in the estimated size of the manifest.
DEFAULT_MAX_NUMBER_TRACK_FILES = 512


class Track(object):
    def __init__(self, files_to_upload, radio):
        self.files_to_upload = files_to_upload
        self.temp_queue = {'data': [], 'number_of_files': 0}
        self.queue = {'data': [], 'number_of_files': 0}
        self.files_to_generate = []
        self.node_request = None
        self.radio = radio
        self.temp = None

    def make_track(self):
        for _file in self.files_to_upload:
            if self.queue['number_of_files'] < DEFAULT_MAX_NUMBER_TRACK_FILES:
                self.queue['data'].append({
                    'name': _file['name'],
                    'size': _file['size'],
                    'path': _file['path'],
                    'metadata_content_type': _file['metadata_content_type'],
                })

                self.temp_queue['data'] = self.queue['data']

                self.queue['number_of_files'] += 1
                self.temp_queue['number_of_files'] = self.queue['number_of_files']

        for _file in self.queue['data']:
            self.files_to_generate.append(_file)

        LOGGER.info('MAKE TRACK QUEUE')

    def upload_track(self, callback_func):
        if not self.temp_queue['data']:
            self.radio.upload_radio(self.radio.upload_radio_callback)  # from WebSite
        else:
            self.temp = self.temp_queue['data'].pop()
            self.node_request.put_file(uri='CHK@',
                                       global_queue=True,
                                       file_path=self.temp['path'],
                                       callback=callback_func)

    def generate_chk_before_upload(self, callback_func):
        if not self.files_to_generate:
            self.upload_track(self.radio.upload_track_callback)  # from WebSite
        else:
            ready = self.files_to_generate.pop()
            self.node_request.put_file(uri='CHK@',
                                       global_queue=True,
                                       file_path=ready['path'],
                                       get_chk_only=True,
                                       callback=callback_func)
