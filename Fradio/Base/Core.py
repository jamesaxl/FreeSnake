from . import vlc
import sqlite3
import configparser
from pathlib import Path, PurePosixPath
from time import gmtime, strftime, localtime
from datetime import datetime

from Fcp.Node import Node
import logging
import uuid
import base64

CONFIG_DIR = '{0}/.config/freeradio'.format(str(Path.home()))

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

DB_FILENAME = '{0}/freeradio.db'.format(CONFIG_DIR)

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG)

# uniqueid is unique between tow users

DB_SCHEMA = '''
create table your_channel (
    id          integer primary key autoincrement not null,
    name   text,
    directory   text,
    create_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    style       text,
    public_key  text unique,
    private_key text unique,
);

create table other_channel (
    id          integer primary key autoincrement not null,
    name   text,
    directory   text,
    create_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    style       text,
    public_key  text unique,
);
'''

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

class Fradio(object):
    '''
    '''

    def __init__(self):
        self.node = Node()
        self.conncet_to_node()

    def create_channel(self, _name, directory):
        pub, prv = self.generate_keys(uri_type = 'USK', name = _name)
        #self.node.node_request.put_directory_files()

    def delete_channel(self, _name):
        pass

    def update_channel(self, _name, directory):
        pass

    def uri_of_channel(self, _name):
        pass

    def load_file(self, _name):
        pass

    def play(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass

    def next(self):
        pass
