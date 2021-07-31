"""
FCP API in Python created by James Axl 2018

For FCP documentation, see https://wiki.freenetproject.org/FCPv2 still under construction
"""

import base64
import configparser
import os
import sys
import uuid
from pathlib import Path

# just for test
current_dir = os.getcwd()
sys.path.append(current_dir)
# just for test

try:
    from Fcp.Node import Node
except ModuleNotFoundError:
    raise ModuleNotFoundError('Fcp module is required')

CONFIG_DIR = '{0}/.config/freesnake/freeradio'.format(str(Path.home()))
CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)
DB_FILENAME = '{0}/freeradio.db'.format(CONFIG_DIR)

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = '9481'
DEFAULT_ENGINE_MODE = 'socket'
DEFAULT_LOG = 'file'


class Core(object):
    def __init__(self):
        Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
        if not Path(CONFIG_FILE).exists():
            self.set_config(
                host=DEFAULT_HOST,
                port=DEFAULT_PORT,
                name_of_connection='freeradio_{0}'.format(self.get_a_uuid()),
                engine_mode=DEFAULT_ENGINE_MODE,
                log=DEFAULT_LOG)

        self.node = Node()

    def get_config(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config['DEFAULT']

    def set_config(self, **config_data):
        config_file = Path(CONFIG_FILE)
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'HOST': config_data['host'],
                             'PORT': config_data['port'],
                             'NAME_OF_CONNECTION': config_data['name_of_connection'],
                             'ENGINE_MODE': config_data['engine_mode'],
                             'LOG': config_data['log']
                             }

        with open(str(config_file), 'w') as configfile:
            config.write(configfile)

    def connect_to_node(self):
        self.node.peer_addr = self.get_config()['HOST']
        self.node.peer_port = int(self.get_config()['PORT'])
        self.node.name_of_connection = self.get_config()['NAME_OF_CONNECTION']
        self.node.engine_mode = self.get_config()['ENGINE_MODE']
        self.node.log = self.get_config()['LOG']
        self.node.connect_to_node()

    def disconnect_from_node(self):
        self.node.disconnect_from_node()

    def get_a_uuid(self, round=3):
        r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
        key = ''
        for i in range(round):
            key += r_uuid.decode().replace('=', '')

        return 'radio_{0}'.format(key)
