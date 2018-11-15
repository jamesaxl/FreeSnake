
# NOTE: Donot use it it still under test

import sqlite3
import configparser
from pathlib import Path
from time import gmtime, strftime

from Fcp.Node import Node # ned to find a good import that will work anywhere

import logging

CONFIG_DIR = '{0}/.config/freesitemgr'.format(str(Path.home()))

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

DB_FILENAME = '{0}/freesitemgr.db'.format(CONFIG_DIR)

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG)

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
    default_index text,
    version     integer not null
);
'''

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

class FsiteMgr(object):

    def __init__(self, host = 'localhost', port = 9481):

        Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
        config_file = Path(CONFIG_FILE)
        db_filename = Path(DB_FILENAME)

        if not db_filename.exists():
            with sqlite3.connect(str(db_filename)) as conn:
                conn.executescript(DB_SCHEMA)
                logging.info('create freesitemgr database schema')

        if not config_file.exists():
            config = configparser.ConfigParser()
            config['DEFAULT'] = {  'HOST' : host, 
                                   'PORT' : port,
                                   'NAME_OF_CONNECTION' : 'freesitemgr'}

            with open(str(config_file), 'w') as configfile:
                config.write(configfile)
                logging.info('create freesitemgr config file')

        self.node.peer_addr = self.get_config()['HOST']
        self.node.peer_port = int(self.get_config()['PORT'])
        self.node.name_of_connection = self.get_config()['NAME_OF_CONNECTION']
        self.node.engine_mode = 'socket'
        self.connect_to_node()

    def get_config(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config['DEFAULT']

    def create_site(self, **kw):
        '''
        site_name: the path that the site will contain
        description: the description of website (optional)
        directory: the directory of site
        default_index: the name of default index ( default is index.html)
        '''

        self.site_name = kw.get('site_name', None)

        if self.check_duplicate(self.site_name):
            logging.info('Site "{0}" already exists'.format(self.site_name))
            return

        self.description = kw.get('description', None)

        self.directory = kw.get('directory', None)

        self.default_index = kw.get('default_index', None)

        self.pub, self.prv = self.node.node_request.generate_keys()

        self.version = 0

        job = self.node.node_request.put_directory(uri = self.prv,
                              uri_type = 'usk',
                              site_name = self.site_name.lower().replace(' ', '_'), directory = self.directory,
                              global_queue = True, persistence = 'forever', 
                              codecs = self.node.compression_codecs,
                              upload_from = 'disk', priority_class = 2, version = self.version,
                              default_index = self.default_index, callback = self.create_site_callback)

        logging.info('Send request "create site" to node')

        return job

    def update_site(self, site_name):
        '''
        site_name the path that the site will contain
        '''

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            update_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM site WHERE site_name = ?; ''', (site_name, ))

            site = cursor.fetchone()

            prv = site[7]
            directory = site[3]
            default_index = site[9]
            self.site_name = site_name
            self.version = site[10] + 1
            conn.commit()
            
            job = self.node.node_request.put_directory(uri = prv,
                                  uri_type = 'usk',,
                                  site_name = self.site_name.lower().replace(' ', '_'), directory = directory,
                                  global_queue = True, persistence = 'forever', 
                                  keep = True, wait_until_sent=False, 
                                  codecs = self.node.compression_codecs,
                                  #dont_compress = True,
                                  upload_from = 'disk',
                                  priority = int(self.get_config()['PRIORITY']), version = self.version,
                                  default_index = default_index, callback = self.update_site_callback)

            logging.info('Send request "update site" to node')

            return job

    def cancel_creation_or_update(self, job):
        job.cancel()

    def delete_site(self, site_name):
        '''
        site_name the path that the site will contain
        '''

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

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM site WHERE site_name = ?; ''', (site_name, ))

            site = cursor.fetchone()
            if site: 
                return {'site_name' : site[1], 'description': site[2],'directory' : site[3],
                        'create_at' : site[4], 'update_at' : site[5], 'public_key' : site[6], 
                        'private_key' : site[7], 'last_uri' : site[8], 'default_index' : site[9],
                        'version' : site[10]}

            return {}

    def get_sites(self):
        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM site; ''')

            sites = cursor.fetchall()
            sites_r = []
            for site in sites:
                sites_r .append({'site_name' : site[1], 'description': site[2],'directory' : site[3],
                        'create_at' : site[4], 'update_at' : site[5], 'public_key' : site[6], 
                        'private_key' : site[7], 'last_uri' : site[8], 'default_index' : site[9],
                        'version' : site[10]})
            
            return sites_r

    def create_site_callback(self, event, result):
        if event == 'successful':
            db_filename = Path(DB_FILENAME)
            with sqlite3.connect(str(db_filename)) as conn:
                update_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                conn.execute('''
                    insert into site (site_name, description, directory, 
                    update_at, public_key, private_key, last_uri, default_index, version)
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?);''', (self.site_name, self.description, 
                                                          self.directory, update_at, self.pub, 
                                                          self.prv, result, self.default_index, self.version))
                conn.commit()
                logging.info('site "{0}" is uploaded'.format(self.site_name))

            #self.node.refresh_persistent_requests()
            self.node.clear_global_job(self._id)
            #self.node.shutdown()
        elif event == 'started_compress':
            logging.info('start compression')

        elif event == 'finished_compress':
            logging.info('finished compression')

        elif event == 'progress':
            self._id = result['Identifier']
            logging.info('upload {0} from {1}'.format(result['Succeeded'], result['Total']))

    def update_site_callback(self, event, result):
        if event == 'successful':
            db_filename = Path(DB_FILENAME)
            with sqlite3.connect(str(db_filename)) as conn:
                update_at = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                conn.execute('''
                    UPDATE site SET last_uri = ? , update_at = ?, version = ? WHERE site_name = ?''', 
                    (result, update_at, self.version, self.site_name))
                
                conn.commit()
                logging.info('site "{0}" is updated'.format(self.site_name))
            
            #self.node.refresh_persistent_requests()
            self.node.clear_global_job(self._id)
            #self.node.shutdown()

        elif event == 'started_compress':
            logging.info('start compression')
        elif event == 'finished_compress':
            logging.info('finished compression')
        elif event == 'progress':
            self._id = result['Identifier']
            logging.info('upload {0} from {1}'.format(result['Succeeded'], result['Total']))
