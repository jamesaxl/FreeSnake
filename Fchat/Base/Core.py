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
import queue

CONFIG_DIR = '{0}/.config/freechat'.format(str(Path.home()))

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

DB_FILENAME = '{0}/freechat.db'.format(CONFIG_DIR)

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG)

# uniqueid is unique between tow users

DB_SCHEMA = '''
create table chat_key (
    id          integer primary key autoincrement not null,
    owner   text,
    friend     text unique,
    create_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    public_key  text unique,
    private_key text unique,
    friend_key  text unique
);

 create table chat_log (
    id          integer primary key autoincrement not null,
    from_nick   text,
    to_nick     text,
    create_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    public_key  text,
    message        text,
    uniqueid       text
);
'''

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

class Fchat(object):
    '''
    Chat Core
    '''

    def __init__(self, host = 'localhost', port = 9481, engine_mode = 'socket', gui = None):
        Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
        config_file = Path(CONFIG_FILE)
        db_filename = Path(DB_FILENAME)

        if not db_filename.exists():
            with sqlite3.connect(str(db_filename)) as conn:
                conn.executescript(DB_SCHEMA)
                logging.info('create freechat database schema')

        if not config_file.exists():
            config = configparser.ConfigParser()
            config['DEFAULT'] = {  'HOST' : host, 
                                   'PORT' : port,
                                   'NAME_OF_CONNECTION' : 'freechat_{0}'.format(str(uuid.uuid4())), 
                                   'ENGINE_MODE' : engine_mode
                                   }

            with open(str(config_file), 'w') as configfile:
                config.write(configfile)
                logging.info('create freechat config file')

        self.node.peer_addr = self.get_config()['HOST']
        self.node.peer_port = int(self.get_config()['PORT'])
        self.node.name_of_connection = self.get_config()['NAME_OF_CONNECTION']
        self.node.engine_mode = 'socket'
        self.connect_to_node()

        self.gui = gui # 

        self.chat_queue = queue.Queue()

    def get_config(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config['DEFAULT']

    def generate_key_for_friend(self, owner, friend):
        pub, prv  = self.node.node_request.generate_keys(uri_type = 'USK', name = owner + '_to_' + friend)
        return pub, prv, owner, friend

    def add_friend(self, pub, prv, owner, friend, friend_key):
        if self.check_friend_duplicate(friend):
            # function for duplicate gui
            return

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            conn.execute('''
                insert into chat_key (owner, friend, 
                public_key, private_key, friend_key)
                values (?, ?, ?, ?, ?);''', (owner, friend, 
                                             pub, prv, friend_key))
            conn.commit()

    def check_friend_duplicate(self, friend):
        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM chat_key WHERE friend = ?; ''', (friend, ))
            chat_key = cursor.fetchone()
            if chat_key[0]:
                return True
            return False


    def send_msg(self, from_nick, to_nick, message):
        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM chat_key WHERE friend = ?; ''', (to_nick, ))

            chat_key = cursor.fetchone()
            message_uri_to_send = chat_key[5]
            
            send_at = strftime('%Y-%m-%dT%H:%M:%S', localtime())
            uniqueid = '{0}_{1}_{2}'.format(from_nick, to_nick, self.get_a_uuid())
            
            chat_buf = ChatTemplate_pb2.Message()

            chat_buf.date_time = send_at
            chat_buf.from_nick = from_nick
            chat_buf.to_nick = to_nick
            chat_buf.message = message
            chat_buf.uniqueid = uniqueid

            if self.chat_queue.empty():
                job = self.node.node_request.put_data( uri = message_uri_to_send,
                                     global_queue = True, persistence = 'forever',
                                     priority = 1, dont_compress = True, data = chat_buf.SerializeToString(),
                                     realtime_flag = True, callback = self.send_msg_callback )

                self.chat_queue.put([from_nick, to_nick, message, uniqueid, send_at, message_uri_to_send])
            else :
                self.chat_queue.put([from_nick, to_nick, message, uniqueid, send_at, message_uri_to_send])

        logging.info('Send request "create a message in the node"')

    def get_msg(self, friend, owner):
        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM chat_key WHERE friend = ? and owner = ?; ''', (friend, owner))
            chat_key = cursor.fetchone()
            self.message_uri_to_get = chat_key[6]
            
            print(self.message_uri_to_get)

            job = self.node.node_request.get( callback = self.get_msg_callback,
                            uri = self.message_uri_to_get,
                            priority_class = 1 )

            return job

    def send_msg_callback(self, event, result):

        if event == 'PutSuccessful':
            chat_data = self.chat_queue.get()
            db_filename = Path(DB_FILENAME)
            with sqlite3.connect(str(db_filename)) as conn:
                conn.execute('''
                
                    insert into chat_log (from_nick, to_nick, 
                    public_key, message, uniqueid)
                    values (?, ?, ?, ?, ?);''', (chat_data[0], chat_data[1], 
                                                 result, chat_data[2], chat_data[3]))
                
                conn.commit()

            print('{}[{}]> {}'.format(chat_data[4], chat_data[0], chat_data[2]))

            if not self.chat_queue.empty():
                chat_data_to_send = self.chat_queue.queue[0]

                chat_buf = ChatTemplate_pb2.Message()
                chat_buf.date_time = chat_data_to_send[4]
                chat_buf.from_nick = chat_data_to_send[0]
                chat_buf.to_nick = chat_data_to_send[1]
                chat_buf.message = chat_data_to_send[2]
                chat_buf.uniqueid = chat_data_to_send[3]
                message_uri_to_send = chat_data_to_send[5]

                job = self.node.node_request.put_data(callback = self.send_msg_callback, uri = message_uri_to_send,
                                     global_queue = True, persistence = 'forever',
                                     priority_class = 1, dont_compress = True, data = chat_buf.SerializeToString(),
                                     real_time_flag = True)

        elif event == 'failed':
            logging.info('transfert is faild please try again')
        else:
            logging.info('Event: {0}'.format(event))

    def get_msg_callback(self, event, result):

        if event == 'AllData':
            chat_buf = ChatTemplate_pb2.Message()
            chat_buf.ParseFromString(result[1])
            
            fmt = '%Y-%m-%dT%H:%M:%S %z'
            zone = strftime('%z', localtime())
            tmconv = strftime('%Y-%m-%dT%H:%M:%S %z', datetime.strptime('{0} {1}'.format(chat_buf.date_time, zone), fmt).utctimetuple())

            db_filename = Path(DB_FILENAME)
            with sqlite3.connect(str(db_filename)) as conn:
                conn.execute('''
                    INSERT INTO chat_log (from_nick, to_nick, 
                    public_key, message, uniqueid)
                    VALUES (?, ?, ?, ?, ?);''', (chat_buf.from_nick, chat_buf.to_nick, 
                                                    self.message_uri_to_get, chat_buf.message, chat_buf.uniqueid))
                conn.commit()

                # execute gui function

        elif event == 'failed':
            logging.info('transfert is faild please try again')
        else:
            logging.info('Event: {0}'.format(event))

    def get_a_uuid(self, round = 3):
        r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
        key = ''
        for i in range(round):
            key += r_uuid.decode().replace('=', '')
        
        return key
