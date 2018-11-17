# -*- coding: utf-8 -*-

# NOTE: Do not use it it still under test

import sqlite3
import configparser
from pathlib import Path, PurePosixPath
from time import gmtime, strftime, localtime
from datetime import datetime

from Fcp.Node import Node
import logging
import uuid
import base64

CONFIG_DIR = '{0}/.config/freetube'.format(str(Path.home()))

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

DB_FILENAME = '{0}/freetube.db'.format(CONFIG_DIR)

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG)

# I will create it after

DB_SCHEMA = '''
create table videos (

);

create table comments (

);

create table views (

);

'''

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)