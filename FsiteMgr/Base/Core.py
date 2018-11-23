# -*- coding: utf-8 -*-

# NOTE: Donot use it it still under test

import sqlite3
import configparser
from pathlib import Path
from time import gmtime, strftime
import base64
import uuid

try:
    from Fcp.Node import Node
except ModuleNotFoundError:
    raise ModuleNotFoundError('Fcp module is required')

import logging

CONFIG_DIR = '{0}/.config/freesnake/freesitemgr'.format(str(Path.home()))

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

DB_FILENAME = '{0}/freesitemgr.db'.format(CONFIG_DIR)

DB_SCHEMA = '''

create table site (
    id          integer primary key autoincrement not null,
    site_name   text unique,
    description text,
    directory   text,
    create_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_at   TIMESTAMP,
    public_key  text unique,
    private_key text unique,
    last_uri    text unique,
    default_name text,
    version     integer not null
);

'''

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = '9481'
DEFAULT_ENGINE_MODE = 'socket'
DEFAULT_VERBOSITY = 'SILENT'
DEFAULT_LOG_TYPE = 'CONSOLE'
DEFAULT_LOG_PATH = '{0}/log'.format(CONFIG_DIR)

class FsiteMgr(object):

    def __init__(self, gui = None):

        Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
        Path(DEFAULT_LOG_PATH).mkdir(parents=True, exist_ok=True)

        db_filename = Path(DB_FILENAME)

        if not db_filename.exists():
            with sqlite3.connect(str(db_filename)) as conn:
                conn.executescript(DB_SCHEMA)
                logging.info('create freesitemgr database schema')

        config_file = Path(CONFIG_FILE)
        if not config_file.exists():
            self.set_config( host = DEFAULT_HOST, 
                             port = DEFAULT_PORT, 
                             name_of_connection = 'freesite_{0}'.format(self.get_a_uuid()),
                             engine_mode = DEFAULT_ENGINE_MODE, 
                             verbosity = DEFAULT_VERBOSITY,
                             log_type = DEFAULT_LOG_TYPE, 
                             log_path = DEFAULT_LOG_PATH)

        self.gui = gui
        self.node = None
        #self.gui.core = self

    def connect(self):
        self.node = Node()
        self.node.peer_addr = self.get_config()['HOST']
        self.node.peer_port = int(self.get_config()['PORT'])
        self.node.name_of_connection = self.get_config()['NAME_OF_CONNECTION']
        self.node.engine_mode = self.get_config()['ENGINE_MODE']
        self.node.verbosity = self.get_config()['VERBOSITY']
        self.node.log_type = self.get_config()['LOG_TYPE']
        self.node.log_path = self.get_config()['LOG_PATH']

        self.node.connect_to_node()

    def disconnect(self):
        self.node.disconnect_from_node()
        del self.node

    def get_config(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config['DEFAULT']

    def set_config(self, **config_data):
        config_file = Path(CONFIG_FILE)
        config = configparser.ConfigParser()
        config['DEFAULT'] = {  'HOST' : config_data['host'], 
                               'PORT' : config_data['port'],
                               'NAME_OF_CONNECTION' : config_data['name_of_connection'], 
                               'ENGINE_MODE' : config_data['engine_mode'],
                               'VERBOSITY' : config_data['verbosity'],
                               'LOG_TYPE' : config_data['log_type'],
                               'LOG_PATH' : config_data['log_path'],  
                            }

        with open(str(config_file), 'w') as configfile:
            config.write(configfile)

        logging.info('Update freesitemgr config file')

    def create_site(self, **kw):
        '''
        site_name: the path that the site will contain
        description: the description of website (optional)
        directory: the directory of site
        default_index: the name of default index ( default is index.html)
        '''

        self.site_name = kw.get('site_name', None)

        if not self.site_name:
            raise Exception('site_name is required')

        self.description = kw.get('description', None)
        if not self.description:
            raise Exception('description is required')

        self.directory = kw.get('directory', None)
        if not self.directory:
            raise Exception('directory is required')

        self.default_name = kw.get('default_name', None)
        if not self.default_name:
            raise Exception('default_name is required')

        if self.check_duplicate(self.site_name):
            logging.info('Site "{0}" already exists'.format(self.site_name))
            return

        self.pub, self.prv = self.node.node_request.generate_keys( uri_type = 'USK', 
                                                                  name = self.site_name.lower().replace(' ', '_'))

        self.version = 0

        job = self.node.node_request.put_complex_directory_files(callback = self.create_site_callback, 
                              uri = self.prv,
                              directory = self.directory,
                              global_queue = True, 
                              persistence = 'forever', 
                              priority_class = 2, 
                              default_name = self.default_name)

        logging.info('Send request "create site" to node')

        return job

    def update_site(self, site_name):
        '''
        site_name the path that the site will contain
        '''

        if not site_name:
            raise Exception('site_name is required')

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            update_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM site WHERE site_name = ?; ''', (site_name, ))

            site = cursor.fetchone()

            prv = site[7]
            directory = site[3]
            default_name = site[9]
            self.site_name = site_name
            self.version = site[10] + 1
            conn.commit()
            
            job = self.node.node_request.put_complex_directory_files(callback = self.update_site_callback, 
                                  uri = prv, 
                                  directory = directory,
                                  global_queue = True, 
                                  persistence = 'forever', 
                                  priority_class = 2, 
                                  default_name= default_name)

            logging.info('Send request "update site" to node')

            return job

    def cancel_creation_or_update(self, job):
        pass

    def delete_site(self, site_name):
        '''
        site_name the path that the site will contain
        '''

        if not site_name:
            raise Exception('site_name is required')

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            update_at = str(datetime.datetime.now())
            cursor  = conn.cursor()
            cursor.execute(''' DELETE FROM site WHERE site_name = ?; ''', (site_name, ))
            logging.info('Delete site "{0}"'.format(site_name))


    def check_duplicate(self, site_name):
        '''
        site_name the path that the site will contain
        '''

        if not site_name:
            raise Exception('site_name is required')

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM site WHERE site_name = ?; ''', (site_name, ))

            site = cursor.fetchone()
            if site: 
                return True

            return False

    def get_site(self, site_name):
        '''
        site_name the path that the site will contain
        '''
        if not site_name:
            raise Exception('site_name is required')

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM site WHERE site_name = ?; ''', (site_name, ))

            site = cursor.fetchone()
            if site: 
                return { 'site_name' : site[1], 'description': site[2],'directory' : site[3],
                        'create_at' : site[4], 'update_at' : site[5], 'public_key' : site[6], 
                        'private_key' : site[7], 'last_uri' : site[8], 'default_index' : site[9],
                        'version' : site[10] }

            return {}

    def get_sites(self):
        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM site; ''')

            sites = cursor.fetchall()
            sites_r = []
            for site in sites:
                sites_r.append({'site_name' : site[1], 'description': site[2],'directory' : site[3],
                        'create_at' : site[4], 'update_at' : site[5], 'public_key' : site[6], 
                        'private_key' : site[7], 'last_uri' : site[8], 'default_index' : site[9],
                        'version' : site[10]})
            
            return sites_r

    def create_site_callback(self, event, result):
        if event == 'PutSuccessful':
            db_filename = Path(DB_FILENAME)
            with sqlite3.connect(str(db_filename)) as conn:
                update_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                conn.execute('''
                    insert into site (site_name, description, directory, 
                    update_at, public_key, private_key, last_uri, default_name, version)
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?);''', (self.site_name, self.description, 
                                                          self.directory, update_at, self.pub, 
                                                          self.prv, result['URI'], self.default_name, self.version ))

                conn.commit()
                logging.info('site "{0}" is uploaded'.format(self.site_name))

        elif event == 'PutFailed':
            logging.info('transfert is faild please try again')

        else:
            logging.info('Event: {0}'.format(event))

    def update_site_callback(self, event, result):
        if event == 'PutSuccessful':
            db_filename = Path(DB_FILENAME)
            with sqlite3.connect(str(db_filename)) as conn:
                update_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                conn.execute('''
                    UPDATE site SET last_uri = ? , update_at = ?, version = ? WHERE site_name = ?''', 
                    (result['URI'], update_at, self.version, self.site_name))

                conn.commit()
                logging.info('site "{0}" is updated'.format(self.site_name))

        elif event == 'PutFailed':
            logging.info('transfert is faild please try again')

        else:
            logging.info('Event: {0}'.format(event))


    def get_a_uuid(self, round = 3):
        r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
        key = ''
        for i in range(round):
            key += r_uuid.decode().replace('=', '')
        
        return key