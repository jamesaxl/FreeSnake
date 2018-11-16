# encoding: utf-8

import queue
import base64
import socket
import time
import uuid
import logging
import threading
from threading import Timer
from pathlib import Path, PurePosixPath
import os
import stat

from .Schema import FromClientToNode
from .Schema import FromNodeToClient
from .Schema import barnamy_parsing_received_request

FCP_VERSION = '2.0'

try:
    import magic
except ModuleNotFoundError:
    raise ModuleNotFoundError('magic module is required')

class Node(object):

    def __init__(self):
        self.__peer_addr = None
        self.__peer_port = None
        self.name_of_connection = None
        self.verbosity = None
        self.connected = False
        self._node_identifier = None

        # socket or wss 
        self.__engine_mode = 'socket'
        self.job_store = self.JobStore()
        self.node_request = None
        self.super_sonic_reactor = None
        
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
            # 
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
        if self.connected:
            raise Exception('You are connected')
        
        self.super_sonic_reactor = self.SuperSonicReactor(self)
        self.node_request = self.NodeRequest(self)
        
        time.sleep(2) # give 2 second to our engine
        
        self.super_sonic_reactor.boost()

        self.node_request.say_hello()

    def disconnect_from_node(self):
        if not self.connected:
            raise Exception('You are not connected')
        self.node_request.disconnect()
        self.connected = False

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

        def say_hello(self):

            if not self.node.name_of_connection:
                self.node.name_of_connection = str(uuid.uuid4())

            if not self.node.verbosity:
                self.node.verbosity = 'SILENT'
                logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=0)
            else:
                if self.node.verbosity == 'DEBUG':
                    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG)

            message = FromClientToNode.client_hello( name = self.node.name_of_connection, 
                                         expected_version = FCP_VERSION)

            self.node.super_sonic_reactor.engine.send_request_to_node(message)
            time.sleep(1)
            self.__watch_global()

        def __watch_global(self):
            message = FromClientToNode.watch_global()
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def generate_keys(self, uri_type = 'SSK', name = None, callback = None):
            self.uri_type = uri_type
            self.name = name
            self.callback = callback

            message, identifier = FromClientToNode.generate_keys()

            job = self.node.JobTicket(self.node)
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

            if uri_type == 'KSK':
                ksk = job.response
                job.__del__()

                return ksk
            
            pub, prv = job.response
            job.__del__()

            return pub, prv

        def test_dda_request(self, **kw):

            message = FromClientToNode.test_dda_request(**kw)

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

        def test_dda_response(self, **kw):
            
            message = FromClientToNode.test_dda_response(**kw)
            
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

        def put_data(self, **kw):

            message, identifier = FromClientToNode.put_data(**kw)

            job = self.node.JobTicket(self.node)

            # __Begin__ add a job
            job.identifier = identifier
            job.callback = None
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.job_store[identifier] = job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def put_file(self, **kw):
            message, identifier = FromClientToNode.put_file(self.node._node_identifier, **kw)
            
            directory = str(PurePosixPath(kw['file_path']).parent)
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
            job.callback = None
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def put_redirect(self, **kw):
            message, identifier = FromClientToNode.put_redirect(**kw)
            job = self.node.JobTicket(self.node)

            # __Begin__ add a job
            job.identifier = identifier
            job.callback = None
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def put_directory_files(self, **kw):
            message, identifier = FromClientToNode.put_directory_files(**kw)
            
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
            job.callback = None
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

         # Still under test
        def put_directory_redirect(self, **kw):
            message, identifier = FromClientToNode.put_directory_redirect(**kw)

            print(message)

        def put_directory_data(self, **kw):
            message, identifier = FromClientToNode.put_directory_data(**kw)

            job = self.node.JobTicket(self.node)
            # __Begin__ add a job
            job.identifier = identifier
            job.callback = None
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job
            
        def get_data(self, **kw):
            message, identifier = FromClientToNode.get_data(**kw)

            # __Begin__ add a job
            job = self.node.JobTicket(self.node)
            job.identifier = identifier
            job.callback = None
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.job_store[identifier] = job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def get_file(self, **kw):
            message, identifier = FromClientToNode.get_file(**kw)
            
            directory = str(PurePosixPath(kw['filename']).parent)
            dda = (directory, False, True)

            if not self._tested_dda.get(dda, False):
                self._tested_dda[dda] = False
                logging.info('We should run test_dda befor getting files')
                self.test_dda_request(directory = directory, read = False, write = True)
          
            time.sleep(2) # Give 2 seconds waiting TestDDAComplete

            # __Begin__ add a job
            job = self.node.JobTicket(self.node)
            job.identifier = identifier
            job.callback = None
            job.message = message
            job.is_file = True
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.job_store[identifier] = job

            self.node.super_sonic_reactor.engine.send_request_to_node(message)

            time.sleep(1)

            return job

        def get_request_status(self, identifier):
            message = FromClientToNode.get_request_status(identifier)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def list_peer(self):
            pass

        def list_peers(self):
            pass

        def list_peer_notes(self):
            pass

        def add_peer(self):
            pass

        def modify_peer(self):
            pass

        def modify_peer_note(self):
            pass

        def remove_peer(self):
            pass

        def get_node(self):
            pass
    
        def get_config(self):
            pass
    
        def modify_config(self):
            pass

        def load_plugin(self):
            pass

        def reload_plugin(self):
            pass

        def remove_plugin(self):
            pass

        def get_plugin_info(self):
            pass

        def fcp_plugin_message(self):
            pass

        def watch_feeds(self):
            pass

        def subscribe_usk(self):
            pass

        def unsubscribe_usk(self):
            pass

        def list_persistent_requests(self):
            pass

        def modify_persistent_request(self):
            pass

        def remove_request(self, identifier):
            message = FromClientToNode.remove_request(identifier)
            self.node.super_sonic_reactor.engine.send_request_to_node(message)

        def disconnect(self):
            message = FromClientToNode.disconnect()
            self.node.super_sonic_reactor.engine.send_request_to_node(message)
            time.sleep(1)
            return

    # The super Sonic Reactor of our Aircraft
    # It is under testing but it works. made by JamesAxl
    # Its nick name is 'Sohoi'
    # Do not touch it please, because the Snake will be hurt :)
    class SuperSonicReactor(object):
        '''

        '''
        def __init__(self, node):
            self.node = node
            self.running = False

            if self.node.engine_mode == 'socket':
                self.engine = self.EngineSocket(self)

            elif self.node.engine_mode == 'ws':
                self.engine = self.EngineWebSocket(self)
            else:
                raise Exception('you mus set socket or wss')

        def boost(self):
            self.engine._connect(self.node.peer_addr, self.node.peer_port)
            self.run()

        def run(self):
            if not self.running:
                self.reactor = Timer(1, self.__reactor, ())
                self.reactor.start()
            else:
                raise Exception('Reactor is running')

        def __shutdown(self):
            self.reactor.cancel()
            self.running = False
            self.engine._close()
            logging.info('Stopping Reactor')
            logging.info('Disconnect from Node')
            self.node.connected = False

        def __reactor(self):
            data = self.engine.listen_to_node()

            if data == ''.encode('utf-8'):
                self.__shutdown()
                return
            
            try:
                p_data = barnamy_parsing_received_request(data)
            except:
                p_data = ['erer', 'erere']
                print(data)
                

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
                        self.node._node_identifier = item['ConnectionIdentifier']
                        logging.info(response)

                elif FromNodeToClient.generate_keys(self.node.node_request.uri_type, self.node.node_request.name, item):
                    identifier, key = FromNodeToClient.generate_keys(self.node.node_request.uri_type, self.node.node_request.name, item)
                    job = self.node.job_store.get(identifier, False) ####
                    if job:
                        # __Begin__ update a job
                        job.response = key
                        job.ready = True
                        # __End__ update a job

                        # callback if yes
                        logging.info('Generate keys')

                elif FromNodeToClient.test_dda_reply(item):
                    
                    write_filename = None
                    read_filename = ''
                    read_content = ''
                    directory = item['Directory']

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

                    print('')
                    logging.info(item)


                elif FromNodeToClient.test_dda_complete(item):
                    print('')
                    logging.info(item)

                elif FromNodeToClient.persistent_put(item):
                    identifier = FromNodeToClient.persistent_put(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        job.response = item
                        # __End__ update a job

                        # callback if yes
                        logging.info('Persistent put')

                elif FromNodeToClient.expected_hashes(item):
                    identifier = FromNodeToClient.expected_hashes(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        #job.response = item
                        # __End__ update a job

                        # callback if yes
                        logging.info('Expected hashes')

                elif FromNodeToClient.finished_compression(item):
                    identifier = FromNodeToClient.finished_compression(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        job.response = item
                        # __End__ update a job
                         
                        logging.info('Compression finished')
                        # callback if yes

                elif FromNodeToClient.uri_generated(item):
                    identifier = FromNodeToClient.uri_generated(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        job.response = item
                        # __End__ update a job

                        # callback if yes
                        logging.info('Uri generated')

                elif FromNodeToClient.simple_progress(item):
                    identifier = FromNodeToClient.simple_progress(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        succeeded = int(item['Succeeded'])
                        required = int(item['Required'])
                        progress = (succeeded / required ) * 100.0

                        job.response = item
                        job.progress= progress
                        # __End__ update a job

                        logging.info('Progress {0:.2f}%'.format(progress))
                        # callback if yes

                elif FromNodeToClient.put_fetchable(item):
                    identifier = FromNodeToClient.put_fetchable(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        job.response = item
                        # __End__ update a job

                        # callback if yes
                        logging.info('Put fetchable')

                elif FromNodeToClient.put_successful(item):
                    identifier = FromNodeToClient.put_successful(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        job.response = item
                        job.ready = True
                        self.node.job_store[identifier].__del__()
                        job.remove_from_queue_when_finish()
                        # __End__ update a job

                        # callback if yes
                        logging.info('Put successful')

                elif FromNodeToClient.put_failed(item):
                    identifier = FromNodeToClient.put_failed(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        job.response = item
                        self.node.job_store[identifier].__del__()
                        job.remove_from_queue_when_finish()
                        # __End__ update a job

                        logging.info('Put failed: {0}'.format(item['CodeDescription']))
                        # callback if yes

                elif FromNodeToClient.persistent_get(item):
                    identifier = FromNodeToClient.persistent_get(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        if item.get('Filename', False):
                            if job.is_file:
                                job.filename = item['Filename']
                        
                        job.response = item
                        # __End__ update a job

                        logging.info('Persistent get')
                        # callback if yes
                     
                elif FromNodeToClient.data_found(item):
                    identifier = FromNodeToClient.data_found(item)
                    job = self.node.job_store.get(identifier, False)####
                    if job:
                        # __Begin__ update a job
                        if job.is_file:
                            data_length = int(item['DataLength']) / 1000000
                            job.response = (job.filename, item['Metadata.ContentType'],'{0:.2f}MB'.format(data_length))
                            self.node.job_store[identifier].__del__()
                            job.remove_from_queue_when_finish()
                        else:
                            job.response = item
                        # __End__ update a job

                        logging.info('Data found')
                        # callback if yes
                elif FromNodeToClient.all_data(item):
                    identifier = FromNodeToClient.all_data(item)
                    job = self.node.job_store.get(identifier, False)####
                    
                    if job:
                        # __Begin__ update a job
                        job.response = item['Metadata.ContentType'], item['Data'], item['DataLength']
                        self.node.job_store[identifier].__del__()
                        job.remove_from_queue_when_finish()
                        # __End__ update a job

                        logging.info('All data')

                elif FromNodeToClient.protocol_error(item):
                    logging.info('Error: {0}'.format(item))

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

            def listen_to_node(self):
                data = self._socket.recv(30000)
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
            self.__max = 10

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
            self.__filename = None

            self.__identifier = None
            self.__request = None
            self.__response = 'Sending'

            self.__callback = None
            self.__ready = False
            self.__progress = 0

            # After
            self.__message = None

            # After
            self.__request = None

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
            self.__node.node_request.remove(self.__identifier)

        def resend(self):
            print(self.__message)

        def remove_from_queue_when_finish(self):
            self.__node.node_request.remove_request(self.__identifier)

        def get_data(self):
            if self.is_file:
                return

            if isinstance(self.__response, dict):
                if self.__response.get('header', False) == 'DataFound':
                    #FIXME: We Should Ask Arnebab Again
                    self.__node.node_request.get_request_status(self.__identifier)
                    self.__node.node_request.get_request_status(self.__identifier)
                    # We Should Ask Arnebab Again
                time.sleep(1)
        