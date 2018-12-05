# -*- coding: utf-8 -*-

# NOTE: Do not use it it still under test

import sqlite3
import configparser
from pathlib import Path, PurePosixPath
from time import gmtime, strftime, localtime
from datetime import datetime
 
try:
    from Fcp.Node import Node
except ModuleNotFoundError:
    raise ModuleNotFoundError('Fcp module is required')

import logging
import uuid
import base64
import queue
from urllib.parse import unquote

from . import ChatTemplate_pb2

CONFIG_DIR = '{0}/.config/freesnake/freechat'.format(str(Path.home()))

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)
INFO_FILE = '{0}/infos'.format(CONFIG_DIR)

DB_FILENAME = '{0}/freechat.db'.format(CONFIG_DIR)

#logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG)

DB_SCHEMA = '''
create table chat_key (
    id                  integer primary key autoincrement not null,
    owner               text,
    friend              text unique,
    create_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    get_message_key          text unique,
    put_message_key         text unique,
    friend_get_message_key  text unique,
    friend_get_status_key   text unique
);

 create table chat_log (
    id              integer primary key autoincrement not null,
    from_nick       text,
    to_nick         text,
    create_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_public_key      text,
    message         text,
    message_version integer
);
'''

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = '9481'
DEFAULT_ENGINE_MODE = 'socket'
DEFAULT_VERBOSITY = 'SILENT'
DEFAULT_LOG_TYPE = 'CONSOLE'
DEFAULT_LOG_PATH = '{0}/log'.format(CONFIG_DIR)

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)

class FchatPrv(object):
    '''
    Chat Core
    '''

    def __init__(self, gui = None):

        Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
        Path(DEFAULT_LOG_PATH).mkdir(parents=True, exist_ok=True)

        config_file = Path(CONFIG_FILE)
        db_filename = Path(DB_FILENAME)

        if not db_filename.exists():
            with sqlite3.connect(str(db_filename)) as conn:
                conn.executescript(DB_SCHEMA)
                logging.info('create freechat database schema')

        if not config_file.exists():
            self.set_config(
                             host = DEFAULT_HOST, 
                             port = DEFAULT_PORT, 
                             name_of_connection = 'freechat_{0}'.format(self.get_a_uuid()),
                             engine_mode = DEFAULT_ENGINE_MODE, 
                             verbosity = DEFAULT_VERBOSITY,
                             log_type = DEFAULT_LOG_TYPE, 
                             log_path = DEFAULT_LOG_PATH )

        self.gui = gui

        #self.gui.core = self

        # Queue for seding messages (message by message) for every user
        self.send_chat_queue = {}
        
        #receive messages from users
        self.get_chat = {}

        # filter Failed put
        self.send_chat_failed = []

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

        logging.info('Update freechat config file')

    def get_friends(self):
        db_filename = Path(DB_FILENAME)
        friends = []
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM chat_key ; ''')
            cursor_r = cursor.fetchall()
            
            for row in cursor_r:
                friends.append(row[2])
            
            return friends

    def change_status(self, status):
        '''
        changing status using USK
        every user has an unique USK Status that can share with friends
        you must share just pub (public key)
        '''

        config = configparser.ConfigParser()
        config.read(INFO_FILE)
        prv = config['STATUS']['PRV']
        
        job = self.node.node_request.put_data( callback = self.change_status_callback, 
                            uri = prv,
                            ignore_usk_datehints = True,
                            global_queue = True, persistence = 'forever',
                            priority_class = 1, dont_compress = True, data = status,
                            real_time_flag = True )

    def check_user_status(self, friend):
        '''
        Check url status of every user using USK
        but before cheking status of your friends 
        you should ask them for pub USK key
        '''
        
        db_filename = Path(DB_FILENAME)
        owner = self.get_info()['OWNER']

        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM chat_key WHERE friend = ? and owner = ?; ''', (friend, owner))
            cursor_r = cursor.fetchone()

            friend_get_status_key = cursor_r[7]

            job = self.node.node_request.get_data( callback = self.check_user_status_callback,
                                uri = friend_get_status_key,
                                priority_class = 1 , global_queue = True)


    def check_unread_message(self, friend):
        '''
        After connecting we should check the last version of USK in database
        and the last USK@ in Freenet Network if they are same, then everything is ok
        if not we should download the unread messages using SSK@
        '''

        pass

    def generate_info(self, name):

        owner = name + '@' + self.get_a_uuid(2)

        info_file = Path(INFO_FILE)
        pub, prv  = self.node.node_request.generate_keys( uri_type = 'USK', name = owner  + '.status' )

        config = configparser.ConfigParser()
        config['INFO'] = {      
                                'OWNER' : owner,
                                'PUB' : pub, 
                                'PRV' : prv,
                            }

        with open(str(info_file), 'w') as infofile:
            config.write(infofile)

    def get_info(self):
        config = configparser.ConfigParser()
        config.read(INFO_FILE)
        return config['INFO']

    def generate_crypt_chat(self, friend):
        '''
        After
        '''
        pass

    def generate_key_for_friend(self):
        '''
        This function will return pub ( that you can give it to your friend )
        and prv ( for sending message to your friend )
        '''
        owner = self.get_info()['OWNER']
        pub, prv  = self.node.node_request.generate_keys( uri_type = 'SSK', name = owner  + '.chat')

        return pub, prv

    def add_friend(self, get_message_key, put_message_key, friend, friend_get_message_key, friend_get_status_key):
        '''
        - get_key: key for retrieving your message (you should give it to your friend)
        - put_key: key for sending message that you generate before
        - friend: the nickname of your friend
        - friend_message_key: pub key of your friend, you use for retrieving message of your friend
        - friend_status_key: pub key of your friend, you can use it for cheking the status of your friend

        NOTE: All these things will be stored in database,
        '''

        owner = self.get_info()['OWNER']

        if self.check_friend_duplicate(friend):

            # function for duplicate gui

            return

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            conn.execute('''
                insert into chat_key (owner, friend, 
                get_message_key, put_message_key, friend_get_message_key, friend_get_status_key)
                values (?, ?, ?, ?, ?, ?);''', ( owner, friend, get_message_key, put_message_key, 
                                                 friend_get_message_key, friend_get_status_key ))

            conn.commit()

    def check_friend_duplicate(self, friend):
        '''
        - friend: nickname of your friend
        '''

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM chat_key WHERE friend = ?; ''', (friend, ))
            cursor_r = cursor.fetchone()

            if cursor_r:
                return True

            return False

    def last_message_version_of_owner_to_send(self, friend):

        db_filename = Path(DB_FILENAME)
        owner = self.get_info()['OWNER']

        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM chat_log WHERE from_nick = ? and to_nick = ? order by id desc LIMIT 1; ''', (owner, friend))
            cursor_r = cursor.fetchone()

            if cursor_r:
                message_version = cursor_r[6]
                return message_version + 1

            return 0

    def send_msg(self, to_nick, message):
        '''
        to_nick: 
        message: 
        '''

        from_nick = self.get_info()['OWNER']

        db_filename = Path(DB_FILENAME)
        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM chat_key WHERE friend = ?; ''', (to_nick, ))

            chat_key = cursor.fetchone()

            get_message_key = chat_key[4]
            put_message_key = chat_key[5]

            send_at = strftime('%Y-%m-%dT%H:%M:%S', localtime())

            message_version = self.last_message_version_of_owner_to_send(to_nick)

            uri_to_send = put_message_key + '-' + str(message_version)

            uri_to_get = get_message_key + '-' + str(message_version)

            if not self.send_chat_queue.get(get_message_key, False):
                self.send_chat_queue[get_message_key] = queue.Queue()

            if self.send_chat_queue[get_message_key].empty():
                chat_buf = ChatTemplate_pb2.Message()

                chat_buf.date_time = send_at
                chat_buf.from_nick = from_nick
                chat_buf.to_nick = to_nick
                chat_buf.message = message
                chat_buf.uniqueid = 'message'

                job = self.node.node_request.put_data( callback = self.send_msg_callback, 
                                     uri = uri_to_send,
                                     global_queue = True, persistence = 'forever',
                                     priority_class = 1, dont_compress = True, 
                                     data = chat_buf.SerializeToString(),
                                     real_time_flag = True, 
                                     extra_inserts_splitfile_header_block = 0 )

                self.send_chat_queue[get_message_key].put({'from_nick' : from_nick, 'to_nick': to_nick, 
                                           'message' : message, 'send_at' : send_at, 'date_time' : send_at,
                                           'put_message_key' : put_message_key})

            else :
                self.send_chat_queue[get_message_key].put({'from_nick' : from_nick, 'to_nick': to_nick, 
                                           'message' : message, 'send_at' : send_at, 'put_message_key' : put_message_key, 
                                           'date_time' : send_at})

        logging.info('Send request \'create a message in the node\'')

    def last_message_version_of_friend_to_get(self, friend):

        db_filename = Path(DB_FILENAME)
        owner = self.get_info()['OWNER']

        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute( ''' SELECT * FROM chat_log WHERE from_nick = ? AND to_nick = ? order by id DESC LIMIT 1; ''', (friend, owner) )
            cursor_r = cursor.fetchone()

            if cursor_r:
                message_version = cursor_r[6]
                return message_version + 1

            return 0

    def get_msg(self, friend):
        '''
        friend: the nickname of your friend
        '''
        db_filename = Path(DB_FILENAME)
        owner = self.get_info()['OWNER']

        with sqlite3.connect(str(db_filename)) as conn:
            cursor  = conn.cursor()
            cursor.execute(''' SELECT * FROM chat_key WHERE friend = ? and owner = ?; ''', (friend, owner))
            chat_key = cursor.fetchone()

            friend_get_message_key = chat_key[6]

            message_version = self.last_message_version_of_friend_to_get(friend)

            uri_to_get = friend_get_message_key + '-' + str(message_version)

            if not self.get_chat.get(friend, False):
                self.get_chat[friend] = uri_to_get

            job = self.node.node_request.get_data( callback = self.get_msg_callback,
                                uri = uri_to_get,
                                priority_class = 1 , global_queue = True)


    def send_msg_callback(self, event, result):

        def _send_msg(get_message_key):
            if not self.send_chat_queue[get_message_key].empty():
                chat_data_to_send = self.send_chat_queue[get_message_key].queue[0]

                chat_buf = ChatTemplate_pb2.Message()
                chat_buf.date_time = chat_data_to_send['date_time']
                chat_buf.from_nick = chat_data_to_send['from_nick']
                chat_buf.to_nick = chat_data_to_send['to_nick']
                chat_buf.message = chat_data_to_send['message']
                chat_buf.uniqueid = 'dfddfef'

                put_message_key = chat_data_to_send['put_message_key']
                
                message_version = self.last_message_version_of_owner_to_send(chat_data_to_send['to_nick'])
                uri_to_send = put_message_key + '-' + str(message_version)

                job = self.node.node_request.put_data( callback = self.send_msg_callback, uri = uri_to_send,
                                    global_queue = True, persistence = 'forever',
                                    priority_class = 1, dont_compress = True, data = chat_buf.SerializeToString(),
                                    real_time_flag = True )
        
        if event == 'PersistentPut':
            if not unquote(result['URI']) in self.send_chat_failed:
                self.send_chat_failed.append(unquote(result['URI']))
        
        if event == 'PutSuccessful':
            url_to_get = unquote(result['URI'])

            #need test
            get_message_key = '-'.join(url_to_get.split('-')[:-1])

            chat_data = self.send_chat_queue[get_message_key].get()
            db_filename = Path(DB_FILENAME)

            # If We are using SSK
            message_version = result['URI'].split('/')[-1].split('-')[-1]

            with sqlite3.connect(str(db_filename)) as conn:
                conn.execute('''

                    INSERT INTO chat_log (from_nick, to_nick, 
                    message_public_key, message, message_version)
                    VALUES (?, ?, ?, ?, ?);''', (chat_data['from_nick'], chat_data['to_nick'], 
                                                 url_to_get, chat_data['message'], message_version))

                conn.commit()

                # execute gui function
                for uri in self.send_chat_failed:
                    if uri == url_to_get:
                        self.send_chat_failed.remove(uri)

                print('{}[{}]> {}'.format(chat_data['date_time'], chat_data['from_nick'], chat_data['message']))

            _send_msg(get_message_key)

        elif event == 'PutFailed':

            # execute gui function
            # resend from queue

            for get_message_key in self.send_chat_failed:
                if not self.send_chat_queue[get_message_key].empty():
                    _send_msg(get_message_key)

            logging.error('transfert is faild please try again')

        else:

            # execute gui function
            logging.info('Event: {0}'.format(event))

    def get_msg_callback(self, event, result):

        if event == 'Data':
            chat_buf = ChatTemplate_pb2.Message()
            
            chat_message = result[0]
            
            try:
                chat_buf.ParseFromString(chat_message)
            except:
                print('someone try to send you no supported msg')
                return

            uri_to_get = self.get_chat[chat_buf.from_nick]

            message_version = uri_to_get.split('/')[-1].split('-')[-1]

            fmt = '%Y-%m-%dT%H:%M:%S %z'
            zone = strftime('%z', localtime())
            tmconv = strftime('%Y-%m-%dT%H:%M:%S %z', datetime.strptime('{0} {1}'.format(chat_buf.date_time, zone), fmt).utctimetuple())

            db_filename = Path(DB_FILENAME)
            with sqlite3.connect(str(db_filename)) as conn:
                conn.execute( '''
                    INSERT INTO chat_log (from_nick, to_nick, 
                    message_public_key, message, message_version)
                    VALUES (?, ?, ?, ?, ?);''', (chat_buf.from_nick, chat_buf.to_nick, 
                                                    uri_to_get, chat_buf.message, 
                                                    message_version) )
                conn.commit()

                print('{}[{}]> {}'.format(chat_buf.date_time, chat_buf.from_nick, chat_buf.message))
                # execute gui function

        elif event == 'GetFaild':
            
            # execute gui function
            # re-check
            
            logging.error('transfert is faild please try again')

        else:
            # execute gui function
            logging.info('Event: {0}'.format(event))

    def change_status_callback(self, event, result):
        if event == 'PutSuccessful':

            print('status changed')
            logging.info('status is changed')
            # execute gui function

        elif event == 'PutFailed':
            logging.info('transfert is faild please try again')
            # execute gui function

        else:
            logging.info('Event: {0}'.format(event))
            # execute gui function

    def check_user_status_callback(self, event, result):
        if event == 'Data':
            # we should know which user
            # execute gui function
            print(result[0].decode('utf-8'))
            logging.info('status is changed')

        elif event == 'GetFaild':
            logging.info('transfert is faild please try again')

        else:
            logging.info('Event: {0}'.format(event))
            # execute gui function

    def get_a_uuid(self, round = 3):
        r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
        key = ''
        for i in range(round):
            key += r_uuid.decode().replace('=', '')

        return key
