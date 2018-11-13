# encoding: utf-8

import queue
import base64
import socket
import time
import uuid
import logging
import threading
from threading import Timer
from pathlib import Path

from .Schema import client_hello_send, client_hello_receive
from .Schema import generate_keys_send, generate_keys_receive
from .Schema import watch_global_send
from .Schema import put_data_send
from .Schema import disconnect_send
from .Schema import get_data_send

from .Schema import parsing_data
from .Schema import persistent_put
from .Schema import expected_hashes
from .Schema import finished_compression
from .Schema import simple_progress
from .Schema import put_fetchable
from .Schema import put_successful
from .Schema import put_failed
from .Schema import persistent_request_removed
from .Schema import uri_generated
from .Schema import remove_data_send

from .Schema import get_request_status_send
from .Schema import persistent_get
from .Schema import data_found
from .Schema import all_data

try:
    import magic
except ModuleNotFoundError:
    raise ModuleNotFoundError('magic module is required')

class Node(object):

    def __init__(self):
        self.peer_addr = None
        self.peer_port = None
        self.name_of_connection = None
        self.verbosity = None
        self.connected = False

        self.node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.node_request = self.NodeRequest(self)
        self.job_store = self.JobStore()
        self.super_sonic_reactor = self.SuperSonicReactor(self)

    class NodeRequest(object):
        def __init__(self, node):
            self.node = node
            self.uri_type = None
            self.name = None

        def connect_to_node(self):
            self.node.node_socket.connect((self.node.peer_addr, self.node.peer_port))
            if not self.node.name_of_connection:
                self.node.name_of_connection = str(uuid.uuid4())

            if not self.node.verbosity:
                self.node.verbosity = 'SILENT'
                logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=0)
            else:
                if self.node.verbosity == 'DEBUG':
                    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.DEBUG)

            self.node.super_sonic_reactor.run()

            self.__hello()
            self.connected = True
            return

        def __hello(self):
            message = client_hello_send( name = self.node.name_of_connection, 
                                         expected_version = '2.0')

            self.node.node_socket.send(message)
            time.sleep(1)

        def __watch_global(self):
            self.node.node_socket.send(watch_global_send())

        def generate_keys(self, uri_type = 'SSK', name = None, callback = None):
            self.uri_type = uri_type
            self.name = name
            self.callback = callback

            message, identifier = generate_keys_send()

            job = self.node.JobTicket(self.node)
            # __Begin__ add a job
            job.identifier = identifier
            job.callback = callback
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.node_socket.send(message)

            time.sleep(1)

            while not job.ready:
                time.sleep(1)

            pub, prv = job.response
            
            job.__del__()

            return pub, prv

        def put_data(self, **kw):
            if kw.get('global_queue', False):
                self.__watch_global()

            message, identifier = put_data_send(**kw)

            job = self.node.JobTicket(self.node)

            # __Begin__ add a job
            job.identifier = identifier
            job.callback = None
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.job_store[identifier] = job

            self.node.node_socket.send(message)

            time.sleep(1)

            return job
 
        def put_file(self, **kw):
            pass

        def put_redirect(self, **kw):
            pass

        def put_directory(self, **kw):
            pass

        def get_data(self, **kw):
            self.__watch_global()

            message, identifier = get_data_send(**kw)

            print (message)
            # __Begin__ add a job
            job = self.node.JobTicket(self.node)
            job.identifier = identifier
            job.callback = None
            job.message = message
            self.node.job_store[identifier] = job
            # __End__ add a job

            self.node.job_store[identifier] = job

            self.node.node_socket.send(message)

            time.sleep(1)

            return job

        def get_request_status(self, identifier):
            self.__watch_global()
            message = get_request_status_send(identifier)
            self.node.node_socket.send(message)


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

        def test_dda_request(self):
            pass

        def test_dda_response(self):
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

        def remove(self, identifier):
            message = remove_data_send(identifier)
            self.node.node_socket.send(message)

        def disconnect_from_node(self):
            message = disconnect_send()
            self.node.node_socket.send(message)
            time.sleep(1)
            self.connected = False
            return

    # The super Sonic Reactor of our Aircraft
    # It is under testing but it works made by JamesAxl
    # Its nick name is 'Sohoi'
    # Do not touch it please, because the Snake will be hurt :)
    class SuperSonicReactor(object):
            def __init__(self, node):
                self.node = node
                self.running = False

            def run(self):
                if not self.running:
                    self.reactor = Timer(1, self.__reactor, ())
                    self.reactor.start()
                else:
                    raise Exception('Reactor is running')

            def __shutdown(self):
                self.reactor.cancel()
                self.running = False
                self.node.node_socket.close()
                logging.info('Disconnected from node')

            def __reactor(self):
                data = self.node.node_socket.recv(30000)

                if data == ''.encode('utf-8'):
                    self.__shutdown()
                    return

                p_data = parsing_data(data)

                for item in p_data:

                    # We need for testing our parsing
                    with open("log.txt", "a") as myfile:
                        myfile.write(str(item))
                        myfile.write('\n\n')

                    if client_hello_receive(item):
                        response = client_hello_receive(item)
                        if response == 'Connection started':
                            self.node.connected = True
                            logging.info(response)

                    elif generate_keys_receive(self.node.node_request.uri_type, self.node.node_request.name, item):
                        identifier, pub, prv = generate_keys_receive(self.node.node_request.uri_type, self.node.node_request.name, item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = (pub, prv)
                            job.ready = True
                            # __End__ update a job

                            # callback if yes
                            logging.info('Generate keys')

                    elif persistent_put(item):
                        identifier = persistent_put(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = item
                            # __End__ update a job

                            # callback if yes
                            logging.info('Persistent put')

                    elif expected_hashes(item):
                        identifier = expected_hashes(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            #job.response = item
                            # __End__ update a job

                            # callback if yes
                            logging.info('Expected hashes')

                    elif finished_compression(item):
                        identifier = finished_compression(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = item
                            # __End__ update a job
                             
                            logging.info('Compression finished')
                            # callback if yes

                    elif uri_generated(item):
                        identifier = uri_generated(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = item
                            # __End__ update a job

                            # callback if yes
                            logging.info('Uri generated')

                    elif simple_progress(item):
                        identifier = simple_progress(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            succeeded = int(item['Succeeded'])
                            required = int(item['Required'])
                            progress = (succeeded / required ) * 100.0

                            job.response = item
                            job.progress= progress
                            # __End__ update a job

                            logging.info('Progress {0}%'.format(progress))
                            # callback if yes

                    elif put_fetchable(item):
                        identifier = put_fetchable(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = item
                            # __End__ update a job

                            # callback if yes
                            logging.info('Put fetchable')

                    elif put_successful(item):
                        identifier = put_successful(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = item
                            job.ready = True
                            self.node.job_store[identifier].__del__()
                            # __End__ update a job

                            # callback if yes
                            logging.info('Put successful')

                    elif put_failed(item):
                        identifier = put_failed(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = item
                            self.node.job_store[identifier].__del__()
                            # __End__ update a job
                            
                            logging.info('Put failed: {0}'.format(item['CodeDescription']))
                            # callback if yes

                    elif persistent_get(item):
                        identifier = persistent_get(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = item
                            # __End__ update a job
                            
                            logging.info('Persistent get')
                            # callback if yes
                         
                    elif data_found(item):
                        identifier = data_found(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = item
                            # __End__ update a job
                            
                            logging.info('Data found')
                            # callback if yes
                    elif all_data(item):
                        identifier = all_data(item)
                        job = self.node.job_store.get(identifier, False)####
                        if job:
                            # __Begin__ update a job
                            job.response = item['Metadata.ContentType'], item['Data'], item['DataLength']
                            self.node.job_store[identifier].__del__()
                            # __End__ update a job
                            logging.info('All data')
                    else:
                        # we need to get the .Schema of every request
                        print(item)


                self.is_running = False
                self.run()

    class JobStore(dict):
        """
        
        """
        def __init__(self):
            super(dict, self).__init__()
            self.__max = 10

        def is_full(self):
            return self.__max == self.keys().__len__()

        def jobs(self):
            return self.keys().__len__()

    class JobTicket(object):
        def __init__(self, node):
            self.__node = node

            self.__identifier = None
            self.__response = 'Sending'
            self.__callback = None
            self.__ready = False
            self.__progress = 0
            self.__message = None
            self.__request = None

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

        def get_data(self):

            #FIXME: We Should Ask Arnebab Again
            self.__node.node_request.get_request_status(self.__identifier)
            self.__node.node_request.get_request_status(self.__identifier)
            # We Should Ask Arnebab Again

            time.sleep(1)
        