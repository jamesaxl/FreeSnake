# encoding: utf-8

try:
    from cerberus import Validator
except ModuleNotFoundError:
    raise ModuleNotFoundError('cerberus module is required')

try:
    from cerberus import Validator
except ModuleNotFoundError:
    raise ModuleNotFoundError('cerberus module is required')


from pathlib import Path, PurePosixPath, PosixPath
import uuid
import base64

class FromClientToNode(object):
    '''
    Requests from client to node
    '''

    # __Begin__ ClientHello
    @staticmethod
    def client_hello(**kw):
        '''
        ClientHello\n
        Name=My Freenet Client\n
        ExpectedVersion=2.0\n
        EndMessage\n
        '''

        name = kw.get('name', None)
        expected_version = kw.get('expected_version', None)

        schema = {'name': {'type' : 'string'}, 'expected_version' : {'type' : 'string'} }

        v = Validator(schema)

        if v.validate(kw):
            client_hello = 'ClientHello\n'
            client_hello += 'Name={0}\n'.format(name)
            client_hello += 'ExpectedVersion={0}\n'.format(expected_version)
            client_hello += 'EndMessage\n'
            return client_hello.encode('utf-8')

        return False

    @staticmethod
    def watch_global():
        watch_global = 'WatchGlobal\n'
        watch_global += 'nIdentifier=__global\n'
        watch_global += 'EndMessage\n'

        return watch_global.encode('utf-8')
    # __End__ WatchGlobal

    # __Begin__ GenerateSSK
    @staticmethod
    def generate_keys():
        '''
        GenerateSSK\n
        Identifier=something\n
        EndMessage\n
        '''
        identifier = get_a_uuid()

        genrate_key = 'GenerateSSK\n'
        genrate_key += 'Identifier={0}\n'.format(identifier)
        genrate_key += 'EndMessage\n'

        return genrate_key.encode('utf-8'), identifier

    # __Begin__ Disconnect
    @staticmethod
    def disconnect():
        '''
        Disconnect\n
        EndMessage\n
        '''

        disconnect = 'Disconnect\n'
        disconnect += 'EndMessage\n'
        return disconnect.encode('utf-8')

    @staticmethod
    def test_dda_request(**kw):
        '''
        TestDDARequest
        Directory=/tmp/
        WantReadDirectory=true
        WantWriteDirectory=true
        EndMessage 
        '''

        schema_succ =   {
                        'directory': {'type' : 'string', 'required': True, 'empty': False},
                        'read' : {'type' : 'boolean', 'required': True, 'empty': False},
                        'write' : {'type' : 'boolean', 'required': True, 'empty': False},
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        test_dda_req = 'TestDDARequest\n'
        test_dda_req += 'Directory={0}\n'.format(kw['directory'])
        test_dda_req += 'WantReadDirectory={0}\n'.format(kw['read'])
        test_dda_req += 'WantWriteDirectory={0}\n'.format(kw['write'])
        test_dda_req += 'EndMessage\n'

        return test_dda_req.encode('utf-8')

    @staticmethod
    def test_dda_response(**kw):
        '''
        TestDDAResponse
        Directory=/tmp/
        ReadContent=Content read from the  "read" file
        EndMessage 
        '''

        schema_succ =   {
                        'directory': {'type' : 'string', 'required': True, 'empty': False},
                        'read_content' : {'type' : 'boolean', 'required': False, 'empty': False},
                        'read_file_name' : {'type' : 'boolean', 'required': False, 'empty': False},
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            return v_succ.errors

        test_dda_res += 'TestDDARequest\n'
        test_dda_res += 'Directory={0}\n'.format(kw['directory'])
        test_dda_res += 'ReadContent={0}\n'.format(kw['read_content'])
        test_dda_res += 'ReadFilename={0}\n'.format(kw['read_file_name'])
        test_dda_res += 'EndMessage\n'

        return test_dda_res

    @staticmethod
    def put_data(**kw):
        '''
        ClientPut\n
        URI=something\n
        Metadata.ContentType=text/html\n
        Identifier=something\n
        Verbosity=0\n
        MaxRetries=10\n
        PriorityClass=1\n
        GetCHKOnly=false\n
        Global=false\n
        DontCompress=false\n
        Codecs=LZMA\n
        TargetFilename\n
        ClientToken=Hello!!!\n
        UploadFrom=direct\n
        LocalRequestOnly=false\n
        Data\n
        Do you want a heavy? Metallica give you heavy baby.\n

        ##########
        
        keywords:
        - uri
        - metadata_content_type
        - verbosity
        - max_retries
        - priority_class
        - get_chk_only
        - global_queue
        - codecs
        - dont_compress
        - client_token
        - persistence
        - target_filename
        - early_encode
        - binary_blob
        - fork_on_cacheable
        - extra_inserts_single_block
        - extra_inserts_splitfile_header_block
        - compatibility_mode
        - local_request_only
        - override_splitfile_crypto_key
        - real_time_flag
        - metadata_threshold
        - data

        for more info https://github.com/freenet/wiki/wiki/FCPv2-ClientPut
        Note: this function is used only from sending direct data, no file and no directory
        '''
    
        put_d = 'ClientPut\n'

        schema_succ =   {
                        'uri': {'type' : 'string', 'required': True, 'empty': False},
                        'metadata_content_type' : {'type' : 'string', 'required': False} ,
                        'verbosity' : {'type' : 'integer' , 'required': False} ,
                        'max_retries' : {'type' : 'integer', 'required': False, 'allowed': range(-1, 999999)} ,
                        'priority_class' : {'type' : 'integer', 'allowed': [0, 1, 2, 3, 4, 5, 6], 'required': False} ,
                        'get_chk_only' : {'type' : 'boolean', 'required': False} ,
                        'global_queue' : {'type' : 'boolean' , 'required': False} ,
                        'codecs' : {'type' : 'string', 'required': False} ,
                        'dont_compress' : {'type' : 'boolean', 'required': False} ,
                        'client_token' : {'type' : 'string', 'required': False} ,
                        'persistence' : {'type' : 'string','allowed': ['connection','forever','reboot'], 'required': False } ,
                        'target_filename' : {'type' : 'string', 'required': False} ,
                        'early_encode' : {'type' : 'boolean', 'required': False} ,
                        'binary_blob' : {'type' : 'boolean', 'required': False} ,
                        'fork_on_cacheable' : {'type' : 'boolean', 'required': False} ,
                        'extra_inserts_single_block' : {'type' : 'integer', 'required': False, 'allowed': range(0, 10)} ,
                        'extra_inserts_splitfile_header_block' : {'type' : 'integer', 'required': False, 'allowed': range(0, 10)} ,
                        'compatibility_mode' : {'type' : 'string', 'required': False} ,
                        'local_request_only' : {'type' : 'boolean', 'required': False} ,
                        'override_splitfile_crypto_key' : {'type' : 'string', 'required': False} ,
                        'real_time_flag' : {'type' : 'boolean', 'required': False} ,
                        'metadata_threshold' : {'type' : 'integer', 'required': False} ,
                        'data' : {'type' : 'string', 'required': True, 'empty': False}
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            return v_succ.errors

        uri = kw.get('uri')
        put_d += 'URI={0}\n'.format(uri)
        
        metadata_content_type = kw.get('metadata_content_type', 'application/octet-stream')
        put_d += 'Metadata.ContentType={0}\n'.format(metadata_content_type)

        identifier = get_a_uuid()
        put_d += 'Identifier={0}\n'.format(identifier)

        verbosity = kw.get('verbosity', 0)
        put_d += 'Verbosity={0}\n'.format(verbosity)

        max_retries = kw.get('max_retries', -1)
        put_d += 'MaxRetries={0}\n'.format(max_retries)
        
        priority_class = kw.get('priority_class', 2)
        put_d += 'PriorityClass={0}\n'.format(priority_class)
        
        get_chk_only = kw.get('get_chk_only', False)
        put_d += 'GetCHKOnly={0}\n'.format(get_chk_only)
        
        global_queue = kw.get('global_queue', False)
        put_d += 'Global={0}\n'.format(global_queue)
        
        dont_compress = kw.get('dont_compress', False)
        put_d += 'DontCompress={0}\n'.format(dont_compress)
        
        if not dont_compress:
            codecs = kw.get('codecs', None)
            if not codecs:
                codecs = 'list of codes'
                put_d += 'Codecs={0}\n'.format(codecs) 
        
        client_token = kw.get('client_token', None)
        if client_token != None:
            put_d += 'ClientToken={0}\n'.format(client_token)

        persistence = kw.get('persistence', 'connection')
        
        if global_queue:
            persistence = 'forever'

        put_d += 'Persistence={0}\n'.format(persistence)

        target_filename = kw.get('target_filename', None)

        early_encode = kw.get('early_encode', False)
        put_d += 'EarlyEncode={0}\n'.format(early_encode)

        upload_from = 'direct'
        put_d += 'UploadFrom={0}\n'.format(upload_from)

        binary_blob = kw.get('binary_blob', False)
        put_d += 'BinaryBlob={0}\n'.format(binary_blob)

        fork_on_cacheable = kw.get('fork_on_cacheable', True)
        put_d += 'ForkOnCacheable={0}\n'.format(fork_on_cacheable)

        extra_inserts_single_block = kw.get('extra_inserts_single_block', None)
        if extra_inserts_single_block != None:
            put_d += 'ExtraInsertsSingleBlock ={0}\n'.format(extra_inserts_single_block)

        extra_inserts_splitfile_header_block = kw.get('extra_inserts_splitfile_header_block', None)
        if extra_inserts_splitfile_header_block != None:
            put_d += 'ExtraInsertsSplitfileHeaderBlock={0}\n'.format(extra_inserts_single_block)

        compatibility_mode = kw.get('compatibility_mode', None)
        if compatibility_mode != None:
            put_d += 'CompatibilityMode={0}\n'.format(compatibility_mode)

        local_request_only = kw.get('local_request_only', False)
        put_d += 'LocalRequestOnly ={0}\n'.format(local_request_only)

        override_splitfile_crypto_key = kw.get('override_splitfile_crypto_key', None)
        if override_splitfile_crypto_key != None:
            put_d += 'OverrideSplitfileCryptoKey ={0}\n'.format(override_splitfile_crypto_key)

        real_time_flag = kw.get('real_time_flag', False)
        put_d += 'RealTimeFlag={0}\n'.format(real_time_flag)

        metadata_threshold = kw.get('metadata_threshold', -1)
        put_d += 'MetadataThreshold ={0}\n'.format(metadata_threshold)

        if global_queue:
            persistence = 'forever'

        data = kw.get('data')
        data_length = len(data.encode('utf-8'))
        put_d += 'DataLength={0}\n'.format(data_length)
        put_d += 'Data\n{0}\n'.format(data)

        return put_data.encode('utf-8'), identifier

    @staticmethod
    def put_file(**kw):
        '''
        ClientPut\n
        URI=something\n
        Metadata.ContentType=text/html\n # you dont need it because magic will do the job
        Identifier=something\n
        Verbosity=0\n
        MaxRetries=10\n
        PriorityClass=1\n
        GetCHKOnly=false\n
        Filename=/home/toad/something.html\n
        TargetFilename=me.html\n
        FileHash=something\n
        Global=false\n
        DontCompress=false\n
        Codecs=LZMA\n
        ClientToken=Hello!!!\n
        UploadFrom=disk\n
        LocalRequestOnly=false\n
        EndMessage\n

        ##########
        
        keywords:
        - uri
        - metadata_content_type
        - verbosity
        - max_retries
        - priority_class
        - get_chk_only
        - global_queue
        - codecs
        - dont_compress
        - client_token
        - persistence
        - target_filename
        - early_encode
        - binary_blob
        - fork_on_cacheable
        - extra_inserts_single_block
        - extra_inserts_splitfile_header_block
        - compatibility_mode
        - local_request_only
        - override_splitfile_crypto_key
        - real_time_flag
        - metadata_threshold
        - file_path
        - node_identifier

        for more info https://github.com/freenet/wiki/wiki/FCPv2-ClientPut
        Note: this function is used only from sending direct data, no file and no directory
        '''

        # It is made by someone (maybe Arnebab).
        # I do not want to touch it
        def sha256dda(node_identifier, identifier, path_of_file):
            """
            returns a sha256 hash of a file's contents for bypassing TestDDA

            >>> oslevelid, filepath = tempfile.mkstemp(text=True)
            >>> with open(filepath, "wb") as f:
            ...     f.write("test")
            >>> print sha256dda("1","2",filepath) == hashlib.sha256("1-2-" + "test").digest()
            True
            """
            tohash = b'-'.join([node_identifier.encode('utf-8'), identifier.encode('utf-8'), open(path_of_file, "rb").read()])
            return hashlib.sha256(tohash).digest()


        put_f = 'ClientPut\n'

        schema_succ =   {
                        'uri': {'type' : 'string', 'required': True, 'empty': False},
                        'verbosity' : {'type' : 'integer' , 'required': False} ,
                        'max_retries' : {'type' : 'integer', 'required': False, 'allowed': range(-1, 999999)} ,
                        'priority_class' : {'type' : 'integer', 'allowed': [0, 1, 2, 3, 4, 5, 6], 'required': False} ,
                        'get_chk_only' : {'type' : 'boolean', 'required': False} ,
                        'global_queue' : {'type' : 'boolean' , 'required': False} ,
                        'codecs' : {'type' : 'string', 'required': False} ,
                        'dont_compress' : {'type' : 'boolean', 'required': False} ,
                        'client_token' : {'type' : 'string', 'required': False} ,
                        'persistence' : {'type' : 'string','allowed': ['connection','forever','reboot'], 'required': False } ,
                        'target_filename' : {'type' : 'string', 'required': False} ,
                        'early_encode' : {'type' : 'boolean', 'required': False} ,
                        'binary_blob' : {'type' : 'boolean', 'required': False} ,
                        'fork_on_cacheable' : {'type' : 'boolean', 'required': False} ,
                        'extra_inserts_single_block' : {'type' : 'integer', 'required': False, 'allowed': range(0, 10)} ,
                        'extra_inserts_splitfile_header_block' : {'type' : 'integer', 'required': False, 'allowed': range(0, 10)} ,
                        'compatibility_mode' : {'type' : 'string', 'required': False} ,
                        'local_request_only' : {'type' : 'boolean', 'required': False} ,
                        'override_splitfile_crypto_key' : {'type' : 'string', 'required': False} ,
                        'real_time_flag' : {'type' : 'boolean', 'required': False} ,
                        'metadata_threshold' : {'type' : 'integer', 'required': False} ,
                        'file_path' : {'type' : 'integer', 'required': True, 'empty': False} ,
                        'node_identifier' : {'type' : 'string', 'required': True, 'empty': False}
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            return v_succ.errors

        uri = kw.get('uri')
        put_f += 'URI={0}\n'.format(uri)
        
        identifier = get_a_uuid()
        put_f += 'Identifier={0}\n'.format(identifier)

        file_path = kw.get('file_path')
        if not PosixPath(file_path).exists():
                raise FileNotFoundError('File not found: {0}'.format(file_path))

        put_f += 'Filename\n{0}'.format(file_path)

        file_hash = base64.b64encode(
                      sha256dda(kw['node_identifier'], identifier, 
                      file_path)).decode('utf-8')

        put_f += 'FileHash={0}\n'.format(file_hash)

        metadata_content_type = magic.from_file(file_path, mime=True).decode()
        put_f += 'Metadata.ContentType={0}\n'.format(metadata_content_type)

        verbosity = kw.get('verbosity', 0)
        put_f += 'Verbosity={0}\n'.format(verbosity)

        max_retries = kw.get('max_retries', -1)
        put_f += 'MaxRetries={0}\n'.format(max_retries)
        
        priority_class = kw.get('priority_class', 2)
        put_f += 'PriorityClass={0}\n'.format(priority_class)
        
        get_chk_only = kw.get('get_chk_only', False)
        put_f += 'GetCHKOnly={0}\n'.format(get_chk_only)
        
        global_queue = kw.get('global_queue', False)
        put_f += 'Global={0}\n'.format(global_queue)
        
        dont_compress = kw.get('dont_compress', False)
        put_f += 'DontCompress={0}\n'.format(dont_compress)

        if not dont_compress:
            codecs = kw.get('codecs', None)
            if not codecs:
                codecs = 'list of codes'
                put_f += 'Codecs={0}\n'.format(codecs)
        
        client_token = kw.get('client_token', None)
        if client_token != None:
            put_f += 'ClientToken={0}\n'.format(client_token)

        persistence = kw.get('persistence', 'connection')

        if global_queue:
            persistence = 'forever'

        put_f += 'Persistence={0}\n'.format(persistence)

        target_filename = kw.get('target_filename', None)

        early_encode = kw.get('early_encode', False)
        put_f += 'EarlyEncode={0}\n'.format(early_encode)

        upload_from = 'direct'
        put_f += 'UploadFrom={0}\n'.format(upload_from)

        binary_blob = kw.get('binary_blob', False)
        put_f += 'BinaryBlob={0}\n'.format(binary_blob)

        fork_on_cacheable = kw.get('fork_on_cacheable', True)
        put_f += 'ForkOnCacheable={0}\n'.format(fork_on_cacheable)

        extra_inserts_single_block = kw.get('extra_inserts_single_block', None)
        if extra_inserts_single_block != None:
            put_f += 'ExtraInsertsSingleBlock ={0}\n'.format(extra_inserts_single_block)

        extra_inserts_splitfile_header_block = kw.get('extra_inserts_splitfile_header_block', None)
        if extra_inserts_splitfile_header_block != None:
            put_f += 'ExtraInsertsSplitfileHeaderBlock={0}\n'.format(extra_inserts_single_block)

        compatibility_mode = kw.get('compatibility_mode', None)
        if compatibility_mode != None:
            put_f += 'CompatibilityMode={0}\n'.format(compatibility_mode)

        local_request_only = kw.get('local_request_only', False)
        put_f += 'LocalRequestOnly ={0}\n'.format(local_request_only)

        override_splitfile_crypto_key = kw.get('override_splitfile_crypto_key', None)
        if override_splitfile_crypto_key != None:
            put_f += 'OverrideSplitfileCryptoKey ={0}\n'.format(override_splitfile_crypto_key)

        real_time_flag = kw.get('real_time_flag', False)
        put_f += 'RealTimeFlag={0}\n'.format(real_time_flag)

        metadata_threshold = kw.get('metadata_threshold', -1)
        put_f += 'MetadataThreshold ={0}\n'.format(metadata_threshold)

        put_f += 'EndMessage\n'

        return put_f.encode('utf-8'), identifier

    @staticmethod
    def put_redirect(self):
        pass

    @staticmethod
    def put_directory(self):
        ''' 
        '''
        pass

    @staticmethod
    def get_data(**kw):
        
        '''
        ClientGet\n
        IgnoreDS=false\n
        DSOnly=false\n
        URI=USK@something\n
        Identifier=Request Number One\n
        Verbosity=0\n
        ReturnType=direct\n
        MaxSize=100\n
        MaxTempSize=1000\n
        MaxRetries=100\n
        PriorityClass=1\n
        Persistence=forever\n
        ClientToken=hello\n
        Global=false\n
        BinaryBlob=false\n
        FilterData=true\n
        EndMessage\n
     
        ###
        keywords:
        - uri
        - ds_only
        - verbosity
        - ignore_ds
        - priority_class
        - max_size
        - global_queue
        - max_temp_size
        - max_retries
        - client_token
        - persistence
        - binary_blob
        - filter_data
        - initial_metadata_data_length
        '''

        get_data = 'ClientGet\n'

        schema_succ =   {

                        'uri': {'type' : 'string', 'required': True, 'empty': False},
                        'ds_only' : {'type' : 'boolean', 'required': False} ,
                        'verbosity' : {'type' : 'integer' , 'required': False} ,
                        'ignore_ds' : {'type' : 'boolean', 'required': False} ,
                        'priority_class' : {'type' : 'integer', 'allowed': [0, 1, 2, 3, 4, 5, 6], 'required': False} ,
                        'max_size' : {'type' : 'integer', 'required': False} ,
                        'global_queue' : {'type' : 'boolean' , 'required': False} ,
                        'max_temp_size' : {'type' : 'integer', 'required': False} ,
                        'max_retries' : {'type' : 'integer', 'required': False} ,
                        'client_token' : {'type' : 'string', 'required': False} ,
                        'persistence' : {'type' : 'string','allowed': ['connection','forever','reboot'], 'required': False } ,
                        'binary_blob' : {'type' : 'boolean', 'required': False} ,
                        'filter_data' : {'type' : 'boolean', 'required': False} ,
                        'initial_metadata_data_length' : {'type' : 'boolean', 'required': False}
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            return v_succ.errors

        identifier = get_a_uuid()

        ignore_ds = kw.get('ignore_ds', False)
        get_data += 'IgnoreDS={}\n'.format(ignore_ds)

        ds_only = kw.get('ds_only', False)
        get_data += 'DSOnly={}\n'.format(ds_only)

        uri = kw['uri']
        get_data += 'URI={}\n'.format(uri)

        global_queue = kw.get('global_queue', False)
        get_data += 'Global={}\n'.format(global_queue)

        get_data += 'Identifier={}\n'.format(identifier)

        persistent = kw.get('persistent', 'connection')

        if global_queue:
            persistent = 'forever'

        get_data += 'Persistence={}\n'.format(persistent)

        priority_class = kw.get('priority_class', 2)
        get_data += 'PriorityClass={}\n'.format(priority_class)

        get_data += 'ReturnType=direct\n'

        filter_data = kw.get('filter_data', False)
        get_data += 'FilterData=false\n'

        get_data += 'EndMessage\n'

        return get_data.encode('utf-8'), identifier 

    @staticmethod
    def get_request_status(identifier):
        '''
        GetRequestStatus\n
        Identifier=something\n
        Persistence=forever\n
        Global=true\n
        EndMessage\n

        ###

        keywords: We will see how to implement
        - persistence
        - global_queue
        '''

        get_request_status =  'GetRequestStatus\n'
        get_request_status += 'Identifier={0}\n'.format(identifier)
        get_request_status += 'Persistence=forever\n'
        get_request_status += 'Global=true\n'
        get_request_status += 'EndMessage\n'

        return get_request_status.encode('utf-8')

    @staticmethod
    def remove_request(identifier):
        '''
        RemovePersistentRequest\n
        Global=true\n
        Identifier=somethimg\n
        EndMessage\n

        ###

        keywords: We will see how to implement
        - persistence
        - global_queue
        '''

        remove_data = 'RemovePersistentRequest\n'
        remove_data += 'Identifier={0}\n'.format(identifier)
        remove_data += 'Global=true\n'
        remove_data += 'EndMessage\n'

        return remove_data.encode('utf-8')


class FromNodeToClient(object):
    '''
    Requests from node to client
    OR
    Received request from node
    '''

    @staticmethod
    def client_hello(data):
        '''
        data received from Node after parsing:

        {'header': 'NodeHello', 'CompressionCodecs': '4 - GZIP(0), BZIP2(1), LZMA(2), LZMA_NEW(3)', 
        'Revision': 'build01481', 'Testnet': 'false', 'Version': 'Fred,0.7,1.0,1481', 
        'Build': '1481', 'ConnectionIdentifier': 'something', 
        'Node': 'Fred', 'ExtBuild': '29', 'FCPVersion': '2.0', 'NodeLanguage': 'C++', 
        'ExtRevision': 'v29', 'footer': 'EndMessage'}
        '''

        parsing_data_generator = data
        
        schema_succ = {
                       'header': {'type' : 'string', 'allowed': ['NodeHello']},
                       'CompressionCodecs' : {'type' : 'string'} ,
                       'Revision' : {'type' : 'string'} ,
                       'Testnet' : {'type' : 'string'} ,
                       'Version' : {'type' : 'string'} ,
                       'Build' : {'type' : 'string'} ,
                       'ConnectionIdentifier' : {'type' : 'string'} ,
                       'Node' : {'type' : 'string'} ,
                       'ExtBuild' : {'type' : 'string'} ,
                       'FCPVersion' : {'type' : 'string'} ,
                       'NodeLanguage' : {'type' : 'string'} ,
                       'ExtRevision' : {'type' : 'string'} ,
                       'footer' : {'type' : 'string'}
                      }


        v_succ = Validator(schema_succ)

        if v_succ.validate(parsing_data_generator):
            return 'Connection started'

        return False

    # __Begin__ ErrorLogin

    @staticmethod
    def protocol_error(data):
        '''
        '''
        schema_succ = {
                   'header': {'type' : 'string', 'allowed': ['ProtocolError']},
                   'footer' : {'type' : 'string'}
                }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return True

        return False
    # __End__ErrorLogin

    # __Begin__ WatchGlobal

    @staticmethod
    def generate_keys(uri_type, name, data):
        '''
        data received from Node after parsing:

        { 'header' : 'SSKKeypair', 'InsertURI' : 'SSK@something', 
        'RequestURI' : ,'Identifier' : 'SSK@Bsomething', 'footer' : 'EndMessage' }
        '''

        parsing_data_generator = data

        schema_uri_type = { 'uri_type': { 'type' : 'string', 'allowed': ['USK', 'SSK', 'KSK']}, 
                            'name' : { 'type' : 'string', 'nullable': True } }

        v_uri_type = Validator(schema_uri_type)
        
        if not v_uri_type.validate({'uri_type' : uri_type, 'name' : name}):
            return False

        schema_succ = {
                        'header': {'type' : 'string'},
                        'InsertURI' : {'type' : 'string'} ,
                        'RequestURI' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(parsing_data_generator):
            private_key = parsing_data_generator['InsertURI']
            public_key = parsing_data_generator['RequestURI']
            identifier = parsing_data_generator['Identifier']

            if uri_type == 'SSK':
                if name:
                    public_key = '{0}{1}/0'.format(parsing_data_generator['RequestURI'], name)
                    private_key = '{0}{1}/0'.format(parsing_data_generator['InsertURI'], name)
                else :
                    public_key = '{0}0'.format(parsing_data_generator['RequestURI'])
                    private_key = '{0}0'.format(parsing_data_generator['InsertURI'])

            elif uri_type == 'USK':
                if name:
                    public_key = '{0}{1}/0'.format(public_key, name)
                    private_key = '{0}{1}/0'.format(private_key, name)
                else:
                    public_key = '{0}0'.format(public_key)
                    private_key = '{0}0'.format(private_key)

                public_key = public_key.replace('SSK', 'USK')
                private_key = private_key.replace('SSK', 'USK')

            elif uri_type == 'KSK':
                if name:
                    return get_a_uuid() + '_' + name

                return get_a_uuid()

            return identifier, public_key, private_key

        return False

    # __End__ GenerateSSK

    @staticmethod
    def test_dda_reply(data):
        '''
        { 'header' : 'TestDDAReply'
        'Directory' : '/tmp/'
        'ReadFilename' : '/tmp/testr.tmp'
        'WriteFilename' : '/tmp/testw.tmp'
        'ContentToWrite' : 'RANDOM'
        'footer' : 'EndMessage' }
        '''
        
        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['TestDDAReply']},
                        'Directory' : {'type' : 'string'} ,
                        'ReadFilename' : {'type' : 'string'} ,
                        'WriteFilename' : {'type' : 'string'} ,
                        'ContentToWrite' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data

        return False

    @staticmethod
    def test_dda_complete(data):
        '''
        { 'header' : 'TestDDAComplete'
        'Directory' : '/tmp/'
        'ReadDirectoryAllowed' : 'true'
        'WriteDirectoryAllowed' : 'true'
        'footer' : 'EndMessage' }
        '''
        
        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['TestDDAComplete']},
                        'Directory' : {'type' : 'string'} ,
                        'ReadFilename' : {'type' : 'string'} ,
                        'WriteFilename' : {'type' : 'string'} ,
                        'ContentToWrite' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data

        return False

    @staticmethod
    def persistent_get(data):
        '''
        data received from Node after parsing:

        {'header': 'PersistentGet', 'Persistence': 'reboot', 
         'MaxRetries': '0', 'BinaryBlob': 'false', 'Started': 
         'false', 'Identifier': 'something', 
         'PriorityClass': '1', 'Verbosity': '0', 'ReturnType': 'direct', 
         'URI': 'SSK@xsomething', 
         'MaxSize': '9223372036854775807', 'Global': 'false', 'RealTime': 'false', 'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['PersistentGet']},
                        'MaxRetries' : {'type' : 'string'} ,
                        'Started' : {'type' : 'string'} ,
                        'PriorityClass' : {'type' : 'string'} ,
                        'BinaryBlob' : {'type' : 'string'} ,
                        'Verbosity' : {'type' : 'string'} ,
                        'URI' : {'type' : 'string'} ,
                        'Persistence' : {'type' : 'string'} ,
                        'RealTime' : {'type' : 'string'} ,
                        'MaxSize' : {'type' : 'string'} ,
                        'ReturnType': {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False
    
    @staticmethod
    def data_found(data):
        '''
        data received from Node after parsing:

        {'header': 'DataFound', 'Identifier': 'something', 
        'CompletionTime': 'something', 'StartupTime': 'something', 
        'DataLength': '29', 'Global': 'false', 'Metadata.ContentType': 'application/octet-stream', 
        'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['DataFound']},
                        'CompletionTime' : {'type' : 'string'} ,
                        'StartupTime' : {'type' : 'string'} ,
                        'DataLength' : {'type' : 'string'} ,
                        'Metadata.ContentType' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def all_data(data):
        '''
        data received from Node after parsing:

        {'header': 'AllData', 'Identifier': 'something', 'CompletionTime': 'something', 
        'StartupTime': 'something', 'DataLength': '29', 'Global': 'true', 'Metadata.ContentType': 
        'application/octet-stream', 'Data': 'testing parsing for 26th timeCompatibilityMode', 'Min': 
        'COMPAT_1416', 'Max': 'COMPAT_1468', 'Definitive': 'true', 
        'SplitfileCryptoKey': 'something', 
        'DontCompress': 'true', 'Min.Number': '6', 'Max.Number': '7', 'footer': 'EndMessage'}
        '''
        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['AllData']},
                        'CompletionTime' : {'type' : 'string'} ,
                        'StartupTime' : {'type' : 'string'} ,
                        'DataLength' : {'type' : 'string'} ,
                        'Metadata.ContentType' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'Data' : {'type' : 'string'} ,
                        'Min' : {'type' : 'string'} ,
                        'Max' : {'type' : 'string'} ,
                        'Definitive' : {'type' : 'string'} ,
                        'SplitfileCryptoKey' : {'type' : 'string'} ,
                        'DontCompress' : {'type' : 'string'} ,
                        'Min.Number' : {'type' : 'string'} ,
                        'Max.Number' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def put_data_receive(data, identifier):
        parsing_data_generator = parsing_data(data)

        for item in parsing_data_generator:
            if item.get('Identifier', None) == identifier:
                yield item

    @staticmethod
    def persistent_put(data):
        '''
        data received from Node after parsing:

        {'header': 'PersistentPut', 'MaxRetries': '-1', 'Started': 'false', 
        'PriorityClass': '2', 'UploadFrom': 'direct', 'CompatibilityMode': 'COMPAT_1468',
         'SplitfileCryptoKey': 'something', 
         'Verbosity': '2147483647', 
         'URI': 'USK@something', 
         'Global': 'true', 'Persistence': 'forever', 
         'Identifier': 'something', 
         'PrivateURI': 'USK@something', 
         'DataLength': '36', 'RealTime': 'true', 'DontCompress': 'true', 'Metadata.ContentType': 'application/octet-stream', 
         'footer': 'EndMessage'}
        '''
        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['PersistentPut']},
                        'MaxRetries' : {'type' : 'string'} ,
                        'Started' : {'type' : 'string'} ,
                        'PriorityClass' : {'type' : 'string'} ,
                        'UploadFrom' : {'type' : 'string'} ,
                        'CompatibilityMode' : {'type' : 'string'} ,
                        'SplitfileCryptoKey' : {'type' : 'string'} ,
                        'Verbosity' : {'type' : 'string'} ,
                        'URI' : {'type' : 'string'} ,
                        'Persistence' : {'type' : 'string'} ,
                        'PrivateURI' : {'type' : 'string'} ,
                        'DataLength' : {'type' : 'string'} ,
                        'RealTime' : {'type' : 'string'} ,
                        'DontCompress' : {'type' : 'string'} ,
                        'Metadata.ContentType' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def expected_hashes(data):
        '''
        data received from Node after parsing:

        {'header': 'ExpectedHashes', 'Identifier': 'something', 
        'Global': 'true', 'Hashes.SHA256': 'something', 
        'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['ExpectedHashes']},
                        'Hashes.SHA256' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def finished_compression(data):
        '''
        data received from Node after parsing:

        {'header': 'FinishedCompression', 
        'Codec': '-1', 'Identifier': 'something', 
        'CompressedSize': '36', 'OriginalSize': '36', 
        'Global': 'true', 'Codec.Name': 'NONE', 'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['FinishedCompression']},
                        'Codec' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'CompressedSize' : {'type' : 'string'} ,
                        'OriginalSize' : {'type' : 'string'} ,
                        'Codec.Name' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def simple_progress(data):
        '''
        data received from Node after parsing:

        {'header': 'SimpleProgress', 'Succeeded': '0', 
         'Identifier': 'something', 
         'Required': '2', 'FinalizedTotal': 'false', 
         'MinSuccessFetchBlocks': '2', 'Failed': '0', 'Total': '2', 
         'LastProgress': 'something', 'FatallyFailed': '0', 
         'Global': 'true', 'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['SimpleProgress']},
                        'Total' : {'type' : 'string'} ,
                        'Required' : {'type' : 'string'} ,
                        'Failed' : {'type' : 'string'} ,
                        'FatallyFailed' : {'type' : 'string'} ,
                        'Succeeded' : {'type' : 'string'} ,
                        'MinSuccessFetchBlocks' : {'type' : 'string'} ,
                        'LastProgress' : {'type' : 'string'} ,
                        'FinalizedTotal' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def uri_generated(data):
        '''
        data received from Node after parsing:

        {'header': 'URIGenerated', 'Identifier': 'something', 
        'URI': 'something', 
        'Global': 'true', 'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['URIGenerated']},
                        'Identifier' : {'type' : 'string'} ,
                        'URI' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def put_fetchable(data):
        '''
        data received from Node after parsing:

        {'header': 'PutFetchable', 'Identifier': 'something', 
        'URI': 'something', 
        'Global': 'true', 'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['PutFetchable']},
                        'URI' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def put_successful(data):
        '''
        data received from Node after parsing:

        {'header': 'PutSuccessful', 'Identifier': 'something', 
        'CompletionTime': 'something', 'StartupTime': 'something', 
        'URI': 'something', 
        'Global': 'true', 'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['PutSuccessful']},
                        'URI' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'CompletionTime' : {'type' : 'string'} ,
                        'StartupTime' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'},
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def put_failed(data):
        '''
        data received from Node after parsing:

        {'header': 'PutFailed', 'Identifier': 'something', 
        'CodeDescription': 'Cancelled by user', 'ShortCodeDescription': 'Cancelled', 
        'Fatal': 'true', 'Code': '10', 'Global': 'true', 'footer': 'EndMessage'}

        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['PutFailed']},
                        'Identifier' : {'type' : 'string'} ,
                        'CodeDescription' : {'type' : 'string'} ,
                        'ShortCodeDescription' : {'type' : 'string'} ,
                        'Fatal' : {'type' : 'string'} ,
                        'Code' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'},
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def persistent_request_removed(data):
        '''
        data received from Node after parsing:

        {'header': 'PersistentRequestRemoved', 
        'Identifier': 'something', 
        'Global': 'true', 'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'allowed': ['PersistentRequestRemoved']},
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string'},
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

# Do not Touch this function if you can not make something better
# Its nickname is Barnamy
def barnamy_parsing_received_request(data):
    data = data.decode().split('\n')
    data_list = []
    data_dic = {}
    iam_data = False

    for item in data:
        if len(item.split('=')) == 1 and item:
            if iam_data:
                data_dic['Data'] = item
                iam_data = False
            elif item == 'EndMessage':
                data_dic['footer'] = item
                if data_dic not in data_list:
                    data_list.append(data_dic)
                data_dic = {}
            elif item == 'Data':
                iam_data = True 
            else:
                data_dic['header'] = item
        elif len(item.split('=')) == 2:
            data_dic[item.split('=')[0]] = item.split('=')[1]

    return data_list

def barnamy_parsing_sent_request(data):
    res = ''
    for k, v in data:
        pass

# Avoid collision. still under test though. I will try to make identify more complex
# We should Ask Arnebab Again
def get_a_uuid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.decode().replace('=', '')

def check_freenet_key(uri):
    # We should ask Arnebab after
    pass
