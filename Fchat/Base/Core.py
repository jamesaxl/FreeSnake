# -*- coding: utf-8 -*-

# NOTE: Do not use it it still under test

import sqlite3
import configparser
from pathlib import Path, PurePosixPath
from time import gmtime, strftime, localtime
from datetime import datetime
import sys, os


#just for test
current_dir = os.getcwd()
sys.path.append(current_dir)
#just for test

try:
    from Fcp.Node import Node
    from Fcp.Node import logger
except ModuleNotFoundError:
    raise ModuleNotFoundError('Fcp module is required')

import uuid
import base64
import queue
from urllib.parse import unquote

from . import ChatTemplate_pb2
from . import AddTemplate_pb2

CONFIG_DIR = '{0}/.config/freesnake/freechat'.format(str(Path.home()))

CONFIG_FILE = '{0}/conf'.format(CONFIG_DIR)
INFO_FILE = '{0}/infos'.format(CONFIG_DIR)

DB_FILENAME = '{0}/freechat.db'.format(CONFIG_DIR)

DB_SCHEMA = '''
create table chat_key (
    id                      integer primary key autoincrement not null,
    owner                   text,
    friend                  text unique,
    create_at               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    get_message_key         text unique,
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

class FchatPrv(object):
    '''
    Chat Core
    '''

    def __init__(self):
        Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
        config_file = Path(CONFIG_FILE)
        db_filename = Path(DB_FILENAME)

        if not db_filename.exists():
            with sqlite3.connect(str(db_filename)) as conn:
                conn.executescript(DB_SCHEMA)
                logger.info('create freechat database schema')

        if not config_file.exists():
            self.set_config(
                             host = DEFAULT_HOST, 
                             port = DEFAULT_PORT, 
                             name_of_connection = 'freechat_{0}'.format(self.get_a_uuid()),
                             engine_mode = DEFAULT_ENGINE_MODE)

        self.node = Node()

        # Queue for seding messages (message by message) for every user
        self.send_chat_queue = {}

        #receive messages from users
        self.get_chat = {}

        # filter Failed put
        self.send_chat_failed = []
        
        # Gui
        self.add_friend_gui = None
        
        logger.info('Welcome to Freenet chat')

    def connect(self):
        self.node.peer_addr = self.get_config()['HOST']
        self.node.peer_port = int(self.get_config()['PORT'])
        self.node.name_of_connection = self.get_config()['NAME_OF_CONNECTION']
        self.node.engine_mode = self.get_config()['ENGINE_MODE']

        self.node.connect_to_node()

    def disconnect(self):
        self.node.disconnect_from_node()

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
                               'ENGINE_MODE' : config_data['engine_mode']
                            }

        with open(str(config_file), 'w') as configfile:
            config.write(configfile)

        logger.info('Update freechat config file')

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
        info_file = Path(INFO_FILE)
        if info_file.exists():
            return
        
        owner = name + '@' + self.get_a_uuid(1)
        pub, prv  = self.node.node_request.generate_keys( uri_type = 'USK', name = owner  + '.status' )

        config = configparser.ConfigParser()
        config['INFO'] = {      
                             'owner' : owner,
                             'status_pub_key' : pub, 
                             'status_prv_key' : prv,
                         }

        with open(str(info_file), 'w') as infofile:
            config.write(infofile)

    def get_info(self):
        info_file = Path(INFO_FILE)
        if not info_file.exists():
            return None

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
        and prv ( for sending message to your friend ) and the last one is pub_info_key
        that contains info about you, not all info of course :).
        '''

        owner = self.get_info()['owner']

        status_pub_key = self.get_info()['status_pub_key']

        pub, prv = self.node.node_request.generate_keys( uri_type = 'SSK', name = owner  + '.chat')

        pub_info_key, prv_info_key = self.node.node_request.generate_keys( uri_type = 'SSK' )

        add_friend_buf = AddTemplate_pb2.Message()
        add_friend_buf.friend = owner
        add_friend_buf.friend_get_message_key = pub
        add_friend_buf.friend_get_status_key = status_pub_key

        job = self.node.node_request.put_data( callback = self.create_info_callback, uri = prv_info_key,
                                     global_queue = True, persistence = 'forever',
                                     priority_class = 1, dont_compress = True, 
                                     data = add_friend_buf.SerializeToString(),
                                     real_time_flag = True, 
                                     extra_inserts_splitfile_header_block = 0 )

        return pub, prv, pub_info_key, job

    def add_friend(self, get_message_key, put_message_key, info_friend_key):
        '''
        - get_message_key: key for retrieving your message (you should give it to your friend)
        - put_message_key: key for sending message that you generate before
        - friend: the nickname of your friend
        - friend_get_message_key: pub key of your friend, you use for retrieving message of your friend
        - friend_get_status_key: pub key of your friend, you can use it for cheking the status of your friend

        NOTE: All these things will be stored in database,
        '''

        job = self.node.node_request.get_data( callback = self.get_info_callback,
                                uri = info_friend_key,
                                priority_class = 1 , global_queue = True)

        self.current_get_message_key = get_message_key
        self.current_put_message_key = put_message_key

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

        logger.info('Send request \'create a message in the node\'')

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

            self.get_chat[friend] = uri_to_get

            print(uri_to_get)

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

            logger.error('transfert is faild please try again')

        else:

            # execute gui function
            logger.info('Event: {0}'.format(event))

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
            
            logger.error('transfert is faild please try again')

        else:
            # execute gui function
            logger.info('Event: {0}'.format(event))

    def change_status_callback(self, event, result):
        if event == 'PutSuccessful':

            print('status changed')
            logger.info('status is changed')
            # execute gui function

        elif event == 'PutFailed':
            logger.info('transfert is faild please try again')
            # execute gui function

        else:
            logger.info('Event: {0}'.format(event))
            # execute gui function

    def check_user_status_callback(self, event, result):
        if event == 'Data':
            # we should know which user
            # execute gui function
            print(result[0].decode('utf-8'))
            logger.info('status is changed')

        elif event == 'GetFaild':
            logger.info('transfert is faild please try again')

        else:
            logger.info('Event: {0}'.format(event))
            # execute gui function

    def create_info_callback(self, event, result):
        
        if event == 'PutSuccessful':
            # we should know which user
            # execute gui function
            # we will get just link
            logger.info('Key is generated {0}'.format(result['URI']))
            self.add_friend_gui.on_generate_keys_ok()

        elif event == 'PutFailed':
            logger.error(result['CodeDescription'])
            self.add_friend_gui.on_generate_keys_faild(result['CodeDescription'])

        else:
            logger.info('Event: {0}'.format(event))
            # execute gui function

    def get_info_callback(self, event, result):
        if event == 'Data':
            # execute gui function
            add_buf = AddTemplate_pb2.Message()

            add_message = result[0]

            # must get the info of owner, get_message_key, put_message_key

            try:
                add_buf.ParseFromString(add_message)
            except:
                print('Someone try to send you no supported msg')
                return

            if self.check_friend_duplicate(add_buf.friend):
                # function for duplicate gui
                self.add_friend_gui.on_save_start_duplicate('{0} exists'.format(add_buf.friend))
                logger.info('{0} exists'.format(add_buf.friend))
                return
            
            owner = self.get_info()['OWNER']

            db_filename = Path(DB_FILENAME)
            with sqlite3.connect(str(db_filename)) as conn:
                conn.execute('''
                    insert into chat_key (owner, friend, 
                    get_message_key, put_message_key, friend_get_message_key, friend_get_status_key)
                    values (?, ?, ?, ?, ?, ?);''', ( owner, add_buf.friend, self.current_get_message_key, self.current_put_message_key, 
                                                     add_buf.friend_get_message_key, add_buf.friend_get_status_key ))

                conn.commit()

            print('{0} is added'.format(add_buf.friend))
            print('{0} is added'.format(add_buf.friend_get_message_key))
            print('{0} is added'.format(add_buf.friend_get_status_key))
            self.add_friend_gui.on_save_start_ok()

        elif event == 'GetFaild':
            self.add_friend_gui.on_save_start_faild()
            logger.error('Can not get info key, please try later')

        else:
            logger.info('Event: {0}'.format(event))
            # execute gui function

    def get_a_uuid(self, round = 3):
        r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
        key = ''
        for i in range(round):
            key += r_uuid.decode().replace('=', '')

        return key
