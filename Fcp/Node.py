# -*- coding: utf-8 -*-

'''
FCP API in Python created by James Axl 2018

For FCP documentation, see http://wiki.freenetproject.org/FCPv2 still under construction
'''

import queue
import base64
import socket
import time
import uuid
import logging
import threading
from threading import Timer
from pathlib import Path, PurePosixPath, PosixPath
import os
import stat
from time import gmtime, strftime, localtime

from .Schema import FromClientToNode
from .Schema import FromNodeToClient
from .Schema import get_a_uuid
from .Schema import barnamy_parsing_received_request_in_bytes

FCP_VERSION = '2.0'

try:
    import magic
except ModuleNotFoundError:
    raise ModuleNotFoundError('magic module is required')

class Node(object):

    def __init__(self):
        self.__peer_addr = None
        self.__peer_port = None
        self.__name_of_connection = None
        self.__verbosity = 'SILENT'
        self.__log_type = 'CONSOLE'
        self.__log_path = '/tmp'
        self.__connected = False
        self.__compression_codecs = None
        self.__node_identifier = None
        self.__engine_mode = 'socket' # socket or wss 
        self.__list_peers = []
        self.__list_peer = None
        self.__node_data = None

        self.job_store = self.JobStore()
        self.node_request = None
        self.super_sonic_reactor = None
        
    @property
    def name_of_connection(self):
        return self.__name_of_connection

    @name_of_connection.setter
    def name_of_connection(self, value):
        self.__name_of_connection = value

    @property
    def verbosity(self):
        return self.__verbosity

    @verbosity.setter
    def verbosity(self, value):
        self.__verbosity = value

    @property
    def log_type(self):
        return self.__log_type

    @log_type.setter
    def log_type(self, value):
        self.__log_type = value

    @property
    def log_path (self):
        return self.__log_path 

    @log_path.setter
    def log_path (self, value):
        self.__log_path = value

    @property
    def connected (self):
        return self.__connected 

    @connected.setter
    def connected (self, value):
        self.__connected = value

    @property
    def compression_codecs (self):
        return self.__compression_codecs

    @compression_codecs.setter
    def compression_codecs(self, value):
        self.__compression_codecs = value


    @property
    def node_identifier (self):
        return self.__node_identifier

    @node_identifier.setter
    def node_identifier(self, value):
        self.__node_identifier = value

    @property
    def node_data(self):
        return self.__node_data

    @node_data.setter
    def node_data(self, value):
        self.__node_data = value

    @property
    def list_peers(self):
        return self.__list_peers

    @list_peers.setter
    def list_peers(self, value):
        self.__list_peers.append(value)

    @list_peers.deleter
    def list_peers(self):
        self.__list_peers.clear()

    @property
    def list_peer(self):
        return self.__list_peer

    @list_peer.setter
    def list_peer(self, value):
        self.__list_peer = value

    @property
    def engine_mode(self):
        return self.__engine_mode

    @engine_mode.setter
    def engine_mode(self, value):
        if not value in ['socket', 'ws']:
            raise Exception('your must set "socket" or "ws"')
        self.__engine_mode = value

    @property
    def peer_addr(self):
        return self.__peer_addr

    @peer_addr.setter
    def peer_addr(self, value):
        self.__peer_addr = value

    @property
    def peer_port(self):
        return self.__peer_port

    @peer_port.setter
    def peer_port(self, value):
        if not isinstance(value, int):
            raise TypeError('peer_port must be integer')
        self.__peer_port = value

    def connect_to_node(self):
        if self.__connected:
            raise Exception('You are connected')

        if not self.__name_of_connection:
            now_is = strftime('%Y-%m-%dT%H-%M-%S', localtime())
            self.__name_of_connection = 'FCP_{0}_{1}'.format(now_is, get_a_uuid())

        if not self.__verbosity in ['SILENT', 'DEBUG']:
            raise Exception('verbosity must be \'SILENT\' or \'DEBUG\'')

        if not self.__log_type in ['CONSOLE', 'FILE']:
            raise Exception('log_type must be \'CONSOLE\' or \'FILE\'')

        if self.__verbosity == 'SILENT':
            # It will show us just errors
            logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.ERROR)

            if self.__log_type == 'FILE':
                if not PosixPath(self.__log_path).exists():
                    raise FileNotFoundError(f'{directory_where_file_log} not found')

                log_file = '{0}/{1}.log'.format(self.__log_path, self.__name_of_connection)
                logging.basicConfig(filename = log_file ,format='%(levelname)s %(asctime)s %(message)s', level=logging.ERROR)

            else:
                logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.ERROR)

        else:
            if self.__log_type == 'FILE':
                if not PosixPath(self.__log_path).exists():
                        raise FileNotFoundError(f'{directory_where_file_log} not found')

                log_file = '{0}/{1}.log'.format(self.__log_path, self.__name_of_connection)
                logging.basicConfig(filename = log_file ,format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG)

            else:
                logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG)

        self.super_sonic_reactor = self.SuperSonicReactor(self)
        self.node_request = self.NodeRequest(self)

        time.sleep(2) # give 2 second to our engine

        self.super_sonic_reactor.boost()

        self.node_request.say_hello()

    def disconnect_from_node(self):
        if not self.__connected:
            raise Exception('You are not connected')

        self.node_request.disconnect()
        self.__connected = False

    def reconnect_to_node(self):
        self.disconnect_from_node()
        # no need to set time sleep.
        # because reactor will bost after 2 second
        self.connect_to_node()

    class NodeRequest(object):
        def __init__(self, node):
            self.node = node
            self.uri_type = None
            self.name = None
            self._tested_dda = {}

        #+ __Begin__ Create connection
        def say_hello(self):

            message = FromClientToNode.client_hello( name = self.node.name_of_connection, 
                                        expected_version = FCP_VERSION)

            self.node.super_sonic_reactor.engine.send_request_to_node(message)
            time.sleep(1)
            self.__watch_global()
        #- __End__ Create connection

#########

        #+ __Begin__ Persistence
        def __watch_global(self):
            message = FromClientToNode.watch_global()
            self.node.super_sonic_reactor.engine.send_request_to_node(message)
        #- __End__ Persistence

#########

        #+ __Begin__ Generate Keys
        def generate_keys(self, callback = None, uri_type = 'SSK', name = None):

            if uri_type == 'KSK':
                if name:
                    ksk = 'KSK@{0}-{1}'.format(get_a_uuid(5), name)
                    if callback:
                        callback('KSKKeypair', ksk)

                    logging.info('Generate keys')
                    return ksk

                ksk = 'KSK@{0}'.format(get_a_uuid(5))
                if callback:
                    callback('KSKKeypair', ksk)

                logging.info('Generate keys')
                return ksk

            message, identifier = FromClientToNode.generate_keys()

            job = self.node.JobTicket(self.node)
            job.response = { 'uri_type' : uri_type, 'name' : name }

            # __Begin__ add a job
            job.identifier = identifier
            job.callback = callback
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            while not job.ready:
                time.sleep(1)

            pub, prv = job.response
            job.__del__()

            return pub, prv
        #- __End__ Generate Keys

#########

        #+ __Begin__ Testing the permission of given directory
        def test_dda_request(self, **kw):

            message = FromClientToNode.test_dda_request(**kw)

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

        def test_dda_response(self, **kw):
            
            message = FromClientToNode.test_dda_response(**kw)
            
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)
        #- __End__ Testing the permission of given directory

#########

        #+ __Begin__ Exchanging data in Freenet
        def put_data(self, callback = None, **kw):

            message, identifier = FromClientToNode.put_data(compression_codecs = self.node.compression_codecs, **kw)

            job = self.node.JobTicket(self.node)

            # __Begin__ add a job
            job.identifier = identifier
            job.callback = callback
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.job_store[identifier] = job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def put_file(self, callback = None, **kw):
            message, identifier = FromClientToNode.put_file(self.node.node_identifier, 
                                                            compression_codecs = self.node.compression_codecs, **kw)

            directory = str(PurePosixPath(kw['file_path']).parent)
            dda = (directory, True, False)

            if not self._tested_dda.get(dda, False):
                self._tested_dda[dda] = False
                logging.info('We should run test_dda befor puting files')
                self.test_dda_request(directory = directory, read = True, write = False)

            time.sleep(2) # Give 2 seconds waiting for TestDDAComplete

            job = self.node.JobTicket(self.node)
            self._tested_dda[dda] = True

            # __Begin__ add a job
            job.identifier = identifier
            job.callback = callback
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def put_redirect(self, callback = None, **kw):
            message, identifier = FromClientToNode.put_redirect(**kw)
            job = self.node.JobTicket(self.node)

            # __Begin__ add a job
            job.identifier = identifier
            job.callback = callback
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def put_complex_directory_files(self, callback = None, **kw):
            message, identifier = FromClientToNode.put_complex_directory_files(compression_codecs = self.node.compression_codecs, **kw)

            directory = kw['directory']
            dda = (directory, True, False)

            if not self._tested_dda.get(dda, False):
                self._tested_dda[dda] = False
                logging.info('We should run test_dda befor puting files')
                self.test_dda_request(directory = directory, read = True, write = False)

            time.sleep(2) # Give 2 seconds waiting TestDDAComplete
            job = self.node.JobTicket(self.node)
            self._tested_dda[dda] = True
            # __Begin__ add a job
            job.identifier = identifier
            job.callback = callback
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

         # Still under test
        def put_complex_directory_redirect(self, callback = None, **kw):
            message, identifier = FromClientToNode.put_complex_directory_redirect(**kw)
            print(message)

        def put_complex_directory_data(self, **kw):
            message, identifier = FromClientToNode.put_complex_directory_data(**kw)

            job = self.node.JobTicket(self.node)
            # __Begin__ add a job
            job.identifier = identifier
            job.callback = callback
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def put_web_site(self, callback = None, **kw):
            '''
            Note: In this function we are going to upload
            website using manifest and separate
            NOTE: we should use it just for websites
            '''
            pass

        def put_radio_channel(self, callback = None, **kw):
            pass

        def put_directory_disk(self, callback = None, **kw):
            message, identifier = FromClientToNode.put_directory_disk(**kw)

            job = self.node.JobTicket(self.node)

            # __Begin__ add a job
            job.identifier = identifier
            job.callback = callback
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def get_data(self, callback = None, **kw):
            message, identifier = FromClientToNode.get_data(**kw)

            # __Begin__ add a job
            job = self.node.JobTicket(self.node)
            job.identifier = identifier
            job.callback = callback

            job.message = kw

            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def get_data_uri_redirect(self, job):
            message, identifier = FromClientToNode.get_data(**job.message)
            
            job.identifier = identifier
            job.ready = False
            self.node.job_store[identifier] = job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def get_stream(self, callback = None, stream = None, **kw):
            message, identifier = FromClientToNode.get_stream(stream, **kw)

            # __Begin__ add a job
            job = self.node.JobTicket(self.node)
            job.identifier = identifier
            job.callback = callback

            job.message = kw
            job.is_stream = True

            job.stream = stream

            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def get_stream_uri_redirect(self, job):
            message, identifier = FromClientToNode.get_stream(**job.message)
            job.identifier = identifier
            job.ready = False
            self.node.job_store[identifier] = job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def get_file(self, callback = None, **kw):
            message, identifier = FromClientToNode.get_file(**kw)
            
            directory = str(PurePosixPath(kw['filename']).parent)
            dda = (directory, False, True)

            if not self._tested_dda.get(dda, False):
                self._tested_dda[dda] = False
                logging.info('We should run test_dda befor getting files')
                self.test_dda_request(directory = directory, read = False, write = True)
          
            time.sleep(2) # Give 2 seconds waiting TestDDAComplete

            # __Begin__ add a job
            self._tested_dda[dda] = True

            job = self.node.JobTicket(self.node)
            job.identifier = identifier
            job.callback = callback
            job.message = kw
            job.is_file = True
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.job_store[identifier] = job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def get_file_uri_redirect(self, job):
            message, identifier = FromClientToNode.get_file(**job.message)
            job.identifier = identifier
            job.ready = False
            self.node.job_store[identifier] = job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def get_request_status(self, identifier):
            message = FromClientToNode.get_request_status(identifier)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)
        #- __End__ Exchanging data in Freenet

#########

        #+ __Begin__ Managing peers
        def list_peer(self, **kw):
            message = FromClientToNode.list_peer(**kw)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def list_peers(self, **kw):
            message = FromClientToNode.list_peers(**kw)
            del(self.node.list_peers)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def list_peer_notes(self, **kw):
            message = FromClientToNode.list_peer_notes(**kw)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def add_peer_from_file(self, **kw):
            message = FromClientToNode.add_peer(**kw)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def add_peer_from_uri(self, **kw):
            message = FromClientToNode.add_peer(**kw)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def add_peer_from_data(self, **kw):
            message = FromClientToNode.add_peer(**kw)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def modify_peer(self, **kw):
            message = FromClientToNode.modify_peer(**kw)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def modify_peer_note(self, **kw):
            message = FromClientToNode.modify_peer_note(**kw)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def remove_peer(self, **kw):
            message = FromClientToNode.remove_peer(**kw)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)
        #- __End__ Managing peers

#########

        #+ __Begin__ Managing Node
        def get_node(self, **kw):
            message = FromClientToNode.get_node(**kw)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)
    
        def get_config(self, **kw):
            '''
            under construction
            '''
            pass
    
        def modify_config(self, **kw):
            '''
            under construction
            '''
            pass
        #- __End__ Managing Node

#########

        #+ __Begin__ Managing Plugins
        def load_plugin(self, **kw):
            message = FromClientToNode.load_plugin(**kw)
            time.sleep(2)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def reload_plugin(self, **kw):
            '''
            under construction
            '''
            pass

        def remove_plugin(self, **kw):
            '''
            under construction
            '''
            pass

        def get_plugin_info(self, **kw):
            '''
            under construction
            '''
            pass

        def fcp_plugin_message(self, **kw):
            '''
            under construction
            '''
            pass
        #- __End__ Managing Plugins

########

        #+ __Begin__ 
        def watch_feeds(self, **kw):
            '''
            under construction
            '''
            pass
        #- __End__ 

#########

        #+ __Begin__ USK
        def subscribe_usk(self, **kw):
            '''
            under construction
            '''
            pass

        def unsubscribe_usk(self, **kw):
            '''
            under construction
            '''
            pass
        #-__End__ USK

#########

        #+ __Begin__ Managing Requests
        def list_persistent_requests(self, **kw):
            '''
            under construction
            '''
            pass

        #def get_request_status(self, **kw):
        #    message = FromClientToNode.get_request_status(identifier)
        #    self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def modify_persistent_request(self, **kw):
            '''
            under construction
            '''
            pass

        def remove_request(self, identifier):
            message = FromClientToNode.remove_request(identifier)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)
        #- __End__ Managing Requests

#########

        #+ __Begin__ Disconnet from node
        def disconnect(self):
            message = FromClientToNode.disconnect()
            self.node.super_sonic_reactor.engine.send_request_to_node(message)
            time.sleep(1)
            return
        #- __End__ Disconnet from node

#########

        #+ __Begin__ Shutdown Node
        def shutdown(self):
            pass
        #- __End__ Shutdown Node

    class SuperSonicReactor(object):
        '''
        Note: The super Sonic Reactor of our Aircraft
        It is under testing but it works. made by JamesAxl
        Its nickname is 'Sohoi'
        Do not touch it please, because the Snake will be hurted :) .
        '''
        def __init__(self, node):
            self.node = node
            self.is_running = False
            self.lock = threading.Lock()

            if self.node.engine_mode == 'socket':
                self.engine = self.EngineSocket(self)

            elif self.node.engine_mode == 'ws':
                self.engine = self.EngineWebSocket(self)
            else:
                raise Exception('you must set socket or ws')


        def boost(self):
            self.engine._connect(self.node.peer_addr, self.node.peer_port)
            self.run()

        def run(self):
            if not self.is_running:
                self.reactor = Timer(1, self.__reactor, ())
                self.reactor.start()
                self.is_running = True
            else:
                raise Exception('Reactor is running')

        def stop(self):
            self.reactor.cancel()
            self.is_running = False

        def __shutdown(self):
            self.stop()
            self.engine._close()
            logging.info('Stopping Reactor')
            logging.info('Disconnect from Node')
            self.node.connected = False

        def read_by_bytes(self, number_of_bytes_to_break):
            '''
            Sonic Boom-One
            It will run When we need to retrieve data
            Without stoping our engine
            '''
            
            buf = bytearray()
            while True:
                c = self.engine.listen_to_node(1)
                buf += c
                if c == b'\n':
                    if buf == b'Data\n':
                        break
                    else:
                        buf = b''

            data_length = 0
            result = bytearray()

            while True:
                data = self.engine.listen_to_node(1)

                data_length += 1
                result += data

                if data_length == number_of_bytes_to_break:
                    break

            return result

        def read_by_bytes_stream(self, number_of_bytes_to_break, our_stream):
            '''
            Sonic Boom-Two
            It will run When we need to retrieve data and put it in a stream
            without stoping our engine
            '''
            buf = bytearray()
            while True:
                c = self.engine.listen_to_node(1)
                buf += c
                if c == b'\n':
                    if buf == b'Data\n':
                        break
                    else:
                        buf = b''

            data_length = 0
            result = bytearray()

            while True:
                data = self.engine.listen_to_node(1)
                data_length += 1
                our_stream.write(data)
                if data_length == number_of_bytes_to_break:
                    break

            our_stream.close()

        def __reactor(self):
            data = self.engine.listen_to_node(32000)

            if data == ''.encode('utf-8'):
                self.__shutdown()
                return

            p_data = barnamy_parsing_received_request_in_bytes(data)

            for item in p_data:

                # We need it for testing our parser
                # We will remove it after
                with open("log.txt", "a") as myfile:
                    myfile.write(str(item))
                    myfile.write('\n\n')

                if FromNodeToClient.client_hello(item):
                    response = FromNodeToClient.client_hello(item)
                    if response == 'Connection started':
                        self.node.connected = True
                        self.node.node_identifier = item['ConnectionIdentifier']
                        
                        self.node.compression_codecs = [(name, int(number[:-1])) 
                                                            for name, number 
                                                            in [i.split("(") 
                                                                for i in item['CompressionCodecs'].split(
                                                                        " - ")[1].split(", ")]]

                        self.node.compression_codecs = ", ".join([name for name, num in self.node.compression_codecs])

                        logging.info(response)

                        # callback

                elif FromNodeToClient.node_data(item):
                    self.node.node_data = item
                    logging.info('{0} {1}'.format(item['header'], item['identity']))

                elif FromNodeToClient.peer(item):
                    self.node.list_peers = item
                    logging.info('{0} {1}'.format(item['header'], item['identity']))

                elif FromNodeToClient.end_list_peers(item):
                    self.node.list_peer = item
                    logging.info('{0}'.format(item['header']))

                elif FromNodeToClient.generate_keys(item):

                    identifier = FromNodeToClient.generate_keys(item)
                    job = self.node.job_store.get(identifier, False) ####
                     
                    if job:

                        # __Begin__ update a job
                        private_key = item['InsertURI']
                        public_key = item['RequestURI']

                        if job.response['uri_type'] == 'SSK':
                            if job.response['name']:
                                public_key = '{0}{1}'.format(item['RequestURI'], job.response['name'])
                                private_key = '{0}{1}'.format(item['InsertURI'], job.response['name'])

                            else :
                                public_key = '{0}'.format(item['RequestURI'])
                                private_key = '{0}'.format(item['InsertURI'])

                        elif job.response['uri_type'] == 'USK':
                            if job.response['name']:
                                public_key = '{0}{1}/0'.format(public_key, job.response['name'])
                                private_key = '{0}{1}/0'.format(private_key, job.response['name'])

                            else:
                                public_key = '{0}0'.format(public_key)
                                private_key = '{0}0'.format(private_key)


                            public_key = public_key.replace('SSK', 'USK')
                            private_key = private_key.replace('SSK', 'USK')

                            item['header'] = 'USKKeypair'


                        job.response = (public_key, private_key)

                        job.ready = True

                        # __End__ update a job

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], job.response)

                        logging.info('Generate keys')

                elif FromNodeToClient.test_dda_reply(item):

                    write_filename = None
                    read_filename = ''
                    read_content = ''
                    directory = item['Directory']

                    if 'ReadFilename' in item:
                        read_filename = item['ReadFilename']

                        if Path(read_filename).exists():
                            read_content = Path(read_filename).read_text('utf-8')
                        else:
                            read_content = ''

                    if 'WriteFilename' in item and 'ContentToWrite' in item:
                        write_filename = item['WriteFilename']
                        content_to_write = item['ContentToWrite']
                        write_file = Path(write_filename)

                        #if write_file.exists():
                        write_file.write_bytes(content_to_write.encode('utf-8'))
                        write_file_stat_object = os.stat(write_filename)
                        write_file_mode = write_file_stat_object.st_mode
                        os.chmod(write_filename, write_file_mode | stat.S_IREAD | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

                    time.sleep(1)
                    self.node.node_request.test_dda_response(directory = directory, 
                                                             read_content = read_content, 
                                                             read_filename = read_filename)

                    if write_filename:
                        if Path(write_filename).exists():
                            file_to_delete = Path(write_filename)
                            file_to_delete.unlink()

                    logging.info(item)

                elif FromNodeToClient.test_dda_complete(item):
                    logging.info(item)

                elif FromNodeToClient.persistent_put(item):
                    identifier = FromNodeToClient.persistent_put(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        if job.callback:
                            job.callback(item['header'], item)

                        logging.info('Persistent put')

                elif FromNodeToClient.expected_hashes(item):
                    identifier = FromNodeToClient.expected_hashes(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                        logging.info('Expected hashes')

                elif FromNodeToClient.started_compression(item):
                    identifier = FromNodeToClient.started_compression(item)
                    job = self.node.job_store.get(identifier, False)
                    if job:
                        logging.info('Compression started')
                        
                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.finished_compression(item):
                    identifier = FromNodeToClient.finished_compression(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        logging.info('Compression finished')
                        
                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.uri_generated(item):
                    identifier = FromNodeToClient.uri_generated(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                        logging.info('Uri generated')

                elif FromNodeToClient.simple_progress(item):
                    identifier = FromNodeToClient.simple_progress(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        succeeded = int(item['Succeeded'])
                        required = int(item['Required'])
                        progress = (succeeded / required ) * 100.0
                        job.progress = round(progress, 2)
                        # __End__ update a job

                        logging.info('Progress {0:.2f}%'.format(progress))
                        
                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.put_fetchable(item):
                    identifier = FromNodeToClient.put_fetchable(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                        logging.info('Put fetchable')

                elif FromNodeToClient.put_successful(item):
                    identifier = FromNodeToClient.put_successful(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        job.response = item
                        job.ready = True
                        job.progress = 100.00
                        job.remove_from_queue_when_finish()
                        # __End__ update a job

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                        logging.info('Put successful')

                elif FromNodeToClient.put_failed(item):
                    identifier = FromNodeToClient.put_failed(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        job.remove_from_queue_when_finish()
                        # __End__ update a job

                        logging.error('Put failed: {0}'.format(item['CodeDescription']))

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.persistent_get(item):
                    identifier = FromNodeToClient.persistent_get(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        if item.get('Filename', False):
                            if job.is_file:
                                job.filename = item['Filename']
                        # __End__ update a job

                        logging.info('Persistent get')

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.data_found(item):
                    identifier = FromNodeToClient.data_found(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # callback if yes
                        if job.callback:
                            job.callback('DataFound', item)

                        # __Begin__ update a job
                        if not job.ready:

                            logging.info('Data found')

                            data_length = item['DataLength']
                            if len(data_length) > 3 and  len(data_length) < 6 :
                                data_length = int(data_length) / 1000
                                data_length = '{0:.2f}Kb'.format(data_length)

                            elif len(data_length) > 6 and  len(data_length) < 9 :
                                data_length = int(data_length) / 1000000
                                data_length = '{0:.2f}Mb'.format(data_length)

                            elif len(data_length) > 9 :
                                data_length = int(data_length) / 1000000000
                                data_length = '{0:.2f}Gb'.format(data_length)

                            else:
                                data_length = int(data_length)
                                data_length = '{0:.2f}b'.format(data_length)


                            if job.is_file:
                                data_length = int(item['DataLength'])
                                job.response = (job.filename, item['Metadata.ContentType'], int(item['DataLength']))
                                logging.info('Metadata.ContentType: {0} || DataLength: {1}'.format(item['Metadata.ContentType'], data_length))
                                job.ready = True

                            elif job.is_stream:
                                self.node.node_request.get_request_status(job.identifier)
                                logging.info('Running Sonic Boom to retrieve Data')

                                self.lock.acquire()
                                self.read_by_bytes_stream(int(item['DataLength']), job.stream)
                                self.lock.release()

                                data_length = int(item['DataLength'])
                                job.response = (job.stream, item['Metadata.ContentType'], int(item['DataLength']))
                                job.ready = True
                                logging.info('Back to the normal stat, Data is ready')

                            else:
                                self.node.node_request.get_request_status(job.identifier)
                                logging.info('Running Sonic Boom to retrieve Data')
                                self.lock.acquire()
                                our_data = self.read_by_bytes(int(item['DataLength']))
                                self.lock.release()

                                job.response = (our_data, item['Metadata.ContentType'], int(item['DataLength']))
                                job.ready = True
                                logging.info('Back to the normal stat, Data is ready')
                                logging.info('Metadata.ContentType: {0} || DataLength: {1}'.format(item['Metadata.ContentType'], data_length))

                        # __End__ update a job

                            job.remove_from_queue_when_finish()

                        # callback if yes
                            if job.callback:
                                job.callback('Data', job.response)

                elif FromNodeToClient.get_failed(item):
                    identifier = FromNodeToClient.get_failed(item)
                    job = self.node.job_store.get(identifier, False)

                    if job:
                        if item.get('RedirectURI', None):

                            logging.warning('Redirect to {}'.format(item['RedirectURI']))

                            job.message['uri'] = item['RedirectURI']

                            if job.message.get('filname', False):
                                self.node.node_request.get_file_uri_redirect(job)

                            elif job.message.get('stream', False):
                                self.node.node_request.get_stream_uri_redirect(job)
                            
                            else:
                                self.node.node_request.get_data_uri_redirect(job)
                            
                            if job.callback:
                                job.callback('RedirectURI', item['RedirectURI'])

                            time.sleep(2)

                            #we should remove the old one
                            self.node.node_request.remove_request(identifier)

                        else:
                            logging.error('Error: {0}'.format(item))
                            if job.callback:
                                job.callback(item['header'], item)

                            job.remove_from_queue_when_finish()

                elif FromNodeToClient.protocol_error(item):
                    
                    result = FromNodeToClient.protocol_error(item)

                    if isinstance(result, str):
                        identifier = result
                        job = self.node.job_store.get(identifier, False)
                        if job:
                            # callback if yes
                            job.callback(item['header'], item)
                            job.response = item
                            del self.node.job_store[identifier]

                    logging.error('Error: {0}'.format(item))

                elif FromNodeToClient.identifier_collision(item):
                    logging.error('Error: {0}'.format(item))

                    # callback if yes
                
                elif FromNodeToClient.sending_to_network(item):
                    identifier = FromNodeToClient.sending_to_network(item)
                    job = self.node.job_store.get(identifier, False)
                    if job:
                        logging.info('{0}'.format(item))

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.expected_hashes(item):

                    identifier = FromNodeToClient.expected_hashes(item)
                    job = self.node.job_store.get(identifier, False)
                    if job:
                        logging.info('{0}'.format(item))

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.compatibility_mode(item):

                    identifier = FromNodeToClient.compatibility_mode(item)
                    job = self.node.job_store.get(identifier, False)
                    if job:
                        logging.info('{0}'.format(item))

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.expected_data_length(item):

                    identifier = FromNodeToClient.expected_data_length(item)
                    job = self.node.job_store.get(identifier, False)
                    if job:
                        logging.info('{0}'.format(item))

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.expected_mime(item):

                    identifier = FromNodeToClient.expected_mime(item)
                    job = self.node.job_store.get(identifier, False)
                    if job:
                        logging.info('{0}'.format(item))

                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                elif FromNodeToClient.persistent_request_removed(item):
                    identifier = FromNodeToClient.persistent_request_removed(item)
                    job = self.node.job_store.get(identifier, False)
                    if job:
                        logging.info('{0}'.format(item))
                        
                        # callback if yes
                        if job.callback:
                            job.callback(item['header'], item)

                        self.node.job_store[identifier].__del__()

                else:
                    # we need to get the Schema of every request
                    print(item)

            self.is_running = False
            self.run()

        class EngineSocket(object):

            def __init__(self, super_sonic_reactor):
                self.super_sonic_reactor = super_sonic_reactor

            def _connect(self, peer_addr, peer_port):
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.connect((peer_addr, peer_port))

            def _close(self):
                self._socket.close()

            def send_request_to_node(self, data):
                self._socket.send(data)

            def listen_to_node(self, number_of_bytes):
                data = self._socket.recv(number_of_bytes)
                return data

        class EngineWebSocket(object):
            try:
                import websockets
            except ModuleNotFoundError:
                raise ModuleNotFoundError('websockets module is required')

            def __init__(self, super_sonic_reactor):
                pass

            def _connect(self):
                pass

            def _close(self):
                pass

            def _send_request(self):
                pass

            def _listen_to_node(self):
                pass

    class JobStore(dict):
        '''
        '''

        def __init__(self):
            super(dict, self).__init__()
            self.__max = 20

        def is_full(self):
            return self.__max == self.keys().__len__()

        def jobs(self):
            return self.keys().__len__()

    class JobTicket(object):
        '''
        '''

        def __init__(self, node):
            self.__node = node

            self.__is_file = False

            self.__is_stream = False

            self.__filename = None
            self.__stream = None

            self.__identifier = None
            self.__request = None
            self.__response = 'Sending'

            self.__callback = None
            self.__ready = False
            self.__progress = 0


            # After: We can need to resend the request 
            # and also to get the type of request
            self.__message = None

        @property
        def stream(self):
            return self.__stream

        @stream.setter
        def stream(self, value):
            self.__stream = value

        @property
        def is_stream(self):
            return self.__is_stream

        @is_stream.setter
        def is_stream(self, value):
            self.__is_stream = value

        @property
        def filename(self):
            return self.__filename

        @filename.setter
        def filename(self, value):
            self.__filename = value

        @property
        def is_file(self):
            return self.__is_file

        @is_file.setter
        def is_file(self, value):
            self.__is_file = value

        @property
        def identifier(self):
            return self.__identifier

        @identifier.setter
        def identifier(self, value):
            self.__identifier = value

        @property
        def message(self):
            return self.__message

        @message.setter
        def message(self, value):
            self.__message = value

        @property
        def response(self):
            return self.__response

        @response.setter
        def response(self, value):
            self.__response = value

        @property
        def callback(self):
            return self.__callback

        @callback.setter
        def callback(self, value):
            self.__callback = value

        @property
        def ready(self):
            return self.__ready

        @ready.setter
        def ready(self, value):
            self.__ready = value

        @property
        def progress(self):
            return self.__progress

        @progress.setter
        def progress(self, value):
            self.__progress = value

        def __del__(self):
            self.__node.job_store.pop(self.identifier, None)

        def cancel(self):
            self.__node.node_request.remove_request(self.__identifier)

        def resend(self):
            print(self.__message)

        def remove_from_queue_when_finish(self):
            time.sleep(2)
            self.__node.node_request.remove_request(self.__identifier)
