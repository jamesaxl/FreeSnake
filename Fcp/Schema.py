# -*- coding: utf-8 -*-

try:
    import cerberus
    from cerberus import Validator
except ModuleNotFoundError:
    raise ModuleNotFoundError('cerberus module is required')

try:
    import magic
except ModuleNotFoundError:
    raise ModuleNotFoundError('magic module is required')


from pathlib import Path, PurePosixPath, PosixPath
import uuid
import base64
import hashlib

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


    @staticmethod
    def list_peer(**kw):
        '''
        ListPeer\n
        NodeIdentifier=[UB] UberNode\n
        WithVolatile=false\n
        WithMetadata=true\n
        EndMessage\n
        '''

        list_p = 'ListPeer\n'

        schema_succ =   {
                        'node_identifier': {'type' : 'string', 'required': True, 'empty': False},
                        'with_volatile' : {'type' : 'boolean', 'required': True, 'empty': False},
                        'with_metadata' : {'type' : 'boolean', 'required': True, 'empty': False},
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        node_identifier = kw['node_identifier']
        list_p += 'NodeIdentifier={0}\n'.fromat(node_identifier)

        with_volatile = kw['with_volatile']
        list_p += 'WithVolatile{0}\n'.fromat(with_volatile)

        with_metadata = kw['with_metadata']
        list_p += 'WithMetadata{0}\n'.fromat(with_metadata)

        list_p += 'EndMessage\n'

        return list_p.encode('utf-8')


    @staticmethod
    def list_peers(**kw):
        '''
        ListPeers\n
        WithVolatile=false\n
        WithMetadata=true\n
        EndMessage\n
        '''

        list_ps = 'ListPeer\n'

        schema_succ =   {
                        'with_volatile' : {'type' : 'boolean', 'required': True, 'empty': False},
                        'with_metadata' : {'type' : 'boolean', 'required': True, 'empty': False},
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        with_volatile = kw['with_volatile']
        list_ps += 'WithVolatile{0}\n'.fromat(with_volatile)

        with_metadata = kw['with_metadata']
        list_ps += 'WithMetadata{0}\n'.fromat(with_metadata)

        list_ps += 'EndMessage\n'

        return list_ps.encode('utf-8')

    @staticmethod
    def list_peer_note(**kw):
        '''
        ListPeerNotes\n
        NodeIdentifier=[UB] UberNode\n
        EndMessage\n
        '''

        list_p_note = 'ListPeerNotes\n'

        schema_succ =   {
                        'node_identifier' : {'type' : 'string', 'required': True, 'empty': False},
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        node_identifier = kw['node_identifier']
        list_ps += 'NodeIdentifier{0}\n'.fromat(node_identifier)

        list_p_note += 'EndMessage\n'

        return list_p_note.encode('utf-8')

    @staticmethod
    def add_peer_from_file(**kw):
        '''
        AddPeer\n
        Trust=HIGH\n
        Visibility=YES\n
        File=newref.txt\n
        EndMessage\n
        '''

        pass

    @staticmethod
    def add_peer_from_uri(**kw):
        '''
        AddPeer\n
        Trust=NORMAL\n
        Visibility=NAME_ONLY\n
        URL=http://foobar.net/myref.txt\n
        EndMessage\n
        '''

        pass

    @staticmethod
    def add_peer_from_data(**kw):
        '''
        AddPeer\n
        Trust=LOW\n
        Visibility=NO\n
        physical.udp=12.34.56.78:12345\n
        lastGoodVersion=Fred,0.7,1.0,874\n
        ark.pubURI=SSK@fjRw9dk...AQABAAE/ark\n
        ark.number=123\n
        identity=GT5~dseFDw...\n
        myName=foobar\n
        base64=true\n
        location=0.01234567890\n
        testnet=false\n
        version=Fred,0.7,1.0,918\n
        EndMessage\n
        '''

        pass

    @staticmethod
    def modify_peer(**kw):
        '''
        ModifyPeer\n
        NodeIdentifier=[UB] UberNode\n
        AllowLocalAddresses=true/false\n
        IsDisabled=true\n
        IsListenOnly=false\n
        IsBurstOnly=false\n
        IgnoreSourcePort=false\n
        EndMessage\n
        '''

        pass

    @staticmethod
    def remove_peer(**kw):
        '''
        RemovePeer
        NodeIdentifier=[UB] UberNode
        EndMessage
        '''

        pass

    @staticmethod
    def get_node(**kw):
        '''
        GetNode
        WithPrivate=true
        WithVolatile=false
        EndMessage
        '''

        pass


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
                        'read_content' : {'type' : 'string', 'required': False},
                        'read_filename' : {'type' : 'string', 'required': False},
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        test_dda_res = 'TestDDAResponse\n'
        test_dda_res += 'Directory={0}\n'.format(kw['directory'])
        test_dda_res += 'ReadContent={0}\n'.format(kw['read_content'])
        test_dda_res += 'ReadFilename={0}\n'.format(kw['read_filename'])
        test_dda_res += 'EndMessage\n'

        return test_dda_res.encode('utf-8')

    @staticmethod
    def put_data(compression_codecs, **kw):
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
        - ignore_usk_datehints
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
                        'ignore_usk_datehints' : {'type' : 'boolean', 'required': False} ,
                        #'data' : {'type' : 'string', 'required': True, 'empty': False}
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            return v_succ.errors

        uri = kw.get('uri')
        put_d += 'URI={0}\n'.format(uri)

        ignore_usk_datehints = kw.get('ignore_usk_date_hints', False)
        put_d += 'IgnoreUSKDatehints={0}\n'.format(ignore_usk_datehints)
        
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
                codecs = compression_codecs

            put_d += 'Codecs={0}\n'.format(codecs)
        
        client_token = kw.get('client_token', None)
        if client_token != None:
            put_d += 'ClientToken={0}\n'.format(client_token)

        persistence = kw.get('persistence', 'connection')
        
        if global_queue:
            persistence = 'forever'

        put_d += 'Persistence={0}\n'.format(persistence)

        target_filename = kw.get('target_filename', None)
        if target_filename:
            put_d += f'TargetFilename={target_filename}\n'

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

        data = kw.get('data', None)

        if not data:
            raise Exception('data field is required')

        data_length = len(data.encode('utf-8'))
        put_d += 'DataLength={0}\n'.format(data_length)
        put_d += 'Data\n{0}\n'.format(data)


        return put_d.encode('utf-8'), identifier

    @staticmethod
    def put_file(node_identifier, **kw):
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
        
        arg:
        - node_identifier

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

        if not node_identifier:
            raise Exception('node_identifier is required')

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
                        'file_path' : {'type' : 'string', 'required': True, 'empty': False} ,
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        uri = kw.get('uri')
        put_f += 'URI={0}\n'.format(uri)
        
        identifier = get_a_uuid()
        put_f += 'Identifier={0}\n'.format(identifier)

        file_path = kw.get('file_path')
        if not PosixPath(file_path).exists():
                raise FileNotFoundError('File not found: {0}'.format(file_path))

        put_f += 'Filename={0}\n'.format(file_path)

        file_hash = base64.b64encode(
                      sha256dda(node_identifier, identifier, 
                      file_path)).decode('utf-8')

        put_f += 'FileHash={0}\n'.format(file_hash)

        metadata_content_type = magic.from_file(file_path, mime=True)
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
                codecs = compression_codecs
            put_f += 'Codecs={0}\n'.format(codecs)
        
        client_token = kw.get('client_token', None)
        if client_token != None:
            put_f += 'ClientToken={0}\n'.format(client_token)

        persistence = kw.get('persistence', 'connection')

        if global_queue:
            persistence = 'forever'

        put_f += 'Persistence={0}\n'.format(persistence)

        target_filename = kw.get('target_filename', None)
        if target_filename:
            put_f += 'TargetFilename={0}\n'.format(target_filename)

        early_encode = kw.get('early_encode', False)
        put_f += 'EarlyEncode={0}\n'.format(early_encode)

        upload_from = 'disk'
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
    def put_redirect(**kw):
        '''
        ClientPut\n
        URI=CHK@\n
        Metadata.ContentType=text/html\n # you dont need it because magic will do the job
        Identifier=something\n
        Verbosity=0\n
        MaxRetries=10\n
        PriorityClass=1\n
        GetCHKOnly=false\n
        TargetURI=something\n
        TargetFilename=me.html\n
        Global=false\n
        DontCompress=false\n
        Codecs=LZMA\n
        ClientToken=Hello!!!\n
        UploadFrom=redirect\n
        LocalRequestOnly=false\n
        EndMessage\n

        ##########
        
        arg:
        - node_identifier

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
        - target_uri

        for more info https://github.com/freenet/wiki/wiki/FCPv2-ClientPut
        Note: this function is used only from sending direct data, no file and no directory
        '''

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
                        'metadata_content_type' : {'type' : 'string', 'required': False} ,
                        'binary_blob' : {'type' : 'boolean', 'required': False} ,
                        'fork_on_cacheable' : {'type' : 'boolean', 'required': False} ,
                        'extra_inserts_single_block' : {'type' : 'integer', 'required': False, 'allowed': range(0, 10)} ,
                        'extra_inserts_splitfile_header_block' : {'type' : 'integer', 'required': False, 'allowed': range(0, 10)} ,
                        'compatibility_mode' : {'type' : 'string', 'required': False} ,
                        'local_request_only' : {'type' : 'boolean', 'required': False} ,
                        'override_splitfile_crypto_key' : {'type' : 'string', 'required': False} ,
                        'real_time_flag' : {'type' : 'boolean', 'required': False} ,
                        'metadata_threshold' : {'type' : 'integer', 'required': False} ,
                        'target_uri' : {'type' : 'string', 'required': True, 'empty': False} ,
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        uri = kw.get('uri')
        put_f += 'URI={0}\n'.format(uri)

        identifier = get_a_uuid()
        put_f += 'Identifier={0}\n'.format(identifier)

        target_uri = kw.get('target_uri')

        put_f += 'TargetURI={0}\n'.format(target_uri)

        metadata_content_type = kw.get('metadata_content_type', 'application/octet-stream')
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
        if target_filename:
            put_f += 'TargetFilename={0}\n'.format(target_filename)

        early_encode = kw.get('early_encode', False)
        put_f += 'EarlyEncode={0}\n'.format(early_encode)

        upload_from = 'redirect'
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
    def put_complex_directory_files(compression_codecs,  **kw):
        ''' 
        ClientPutComplexDir\n
        URI=something@\n
        Identifier=something\n
        Verbosity=0\n
        MaxRetries=10\n
        PriorityClass=1\n
        GetCHKOnly=false\n
        Global=false\n
        DontCompress=true\n
        ClientToken=Hello!!!\n
        LocalRequestOnly=false\n
        DefaultName=name\n
        Files.N.Name=file name\n
        Files.N.UploadFrom=disk\n
        Files.N.Filename=path/of/filename\n
        Files.N.Metadata.ContentType\n  # You dont need it because magic will do the job :)
        EndMessage\n

        ##########

        keywords:
        - uri
        - verbosity
        - max_retries
        - priority_class
        - get_chk_only
        - global_queue
        - codecs
        - dont_compress
        - client_token
        - persistence
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
        - directory
        - site_name
        - default_name: Default index, e.g index.html if you set name 
                        of file that not exists in directory you are going to have an exception

        for more info https://github.com/freenet/wiki/wiki/FCPv2-ClientPutComplexDir
        Note: this function is used only from sending direct data, no file and no directory
        '''

        put_directory_f = 'ClientPutComplexDir\n'

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
                        'default_name' : {'type' : 'string', 'required': False} ,
                        'directory' : {'type' : 'string', 'required': True, 'empty': False} ,
                        'site_name' : {'type' : 'string', 'required': False, 'empty': False} ,
                    }

        v_succ = Validator(schema_succ)
        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        default_name = kw['default_name']
        directory = kw['directory']

        if not PosixPath('{0}/{1}'.format(directory, default_name)).exists():
            raise FileNotFoundError('File not found: {0}'.format(default_name))

        site_name = kw.get('kw', False)

        uri = kw.get('uri')

        put_directory_f += 'URI={0}\n'.format(uri)

        identifier = get_a_uuid()
        put_directory_f += 'Identifier={0}\n'.format(identifier)

        verbosity = kw.get('verbosity', 0)
        put_directory_f += 'Verbosity={0}\n'.format(verbosity)

        max_retries = kw.get('max_retries', -1)
        put_directory_f += 'MaxRetries={0}\n'.format(max_retries)

        priority_class = kw.get('priority_class', 2)
        put_directory_f += 'PriorityClass={0}\n'.format(priority_class)

        get_chk_only = kw.get('get_chk_only', False)
        put_directory_f += 'GetCHKOnly={0}\n'.format(get_chk_only)

        global_queue = kw.get('global_queue', False)
        put_directory_f += 'Global={0}\n'.format(global_queue)

        dont_compress = kw.get('dont_compress', False)
        put_directory_f += 'DontCompress={0}\n'.format(dont_compress)

        if not dont_compress:
            codecs = kw.get('codecs', None)
            if not codecs:
                codecs = compression_codecs
                put_directory_f += 'Codecs={0}\n'.format(codecs)

        client_token = kw.get('client_token', None)
        if client_token != None:
            put_directory_f += 'ClientToken={0}\n'.format(client_token)

        persistence = kw.get('persistence', 'connection')

        if global_queue:
            persistence = 'forever'

        put_directory_f += 'Persistence={0}\n'.format(persistence)

        target_filename = kw.get('target_filename', None)
        if target_filename:
            put_directory_f += 'TargetFilename={0}\n'.format(target_filename)

        early_encode = kw.get('early_encode', False)
        put_directory_f += 'EarlyEncode={0}\n'.format(early_encode)

        binary_blob = kw.get('binary_blob', False)
        put_directory_f += 'BinaryBlob={0}\n'.format(binary_blob)

        fork_on_cacheable = kw.get('fork_on_cacheable', True)
        put_directory_f += 'ForkOnCacheable={0}\n'.format(fork_on_cacheable)

        extra_inserts_single_block = kw.get('extra_inserts_single_block', None)
        if extra_inserts_single_block != None:
            put_directory_f += 'ExtraInsertsSingleBlock ={0}\n'.format(extra_inserts_single_block)

        extra_inserts_splitfile_header_block = kw.get('extra_inserts_splitfile_header_block', None)
        if extra_inserts_splitfile_header_block != None:
            put_directory_f += 'ExtraInsertsSplitfileHeaderBlock={0}\n'.format(extra_inserts_single_block)

        compatibility_mode = kw.get('compatibility_mode', None)
        if compatibility_mode != None:
            put_directory_f += 'CompatibilityMode={0}\n'.format(compatibility_mode)

        local_request_only = kw.get('local_request_only', False)
        put_directory_f += 'LocalRequestOnly ={0}\n'.format(local_request_only)

        override_splitfile_crypto_key = kw.get('override_splitfile_crypto_key', None)
        if override_splitfile_crypto_key != None:
            put_directory_f += 'OverrideSplitfileCryptoKey ={0}\n'.format(override_splitfile_crypto_key)

        real_time_flag = kw.get('real_time_flag', False)
        put_directory_f += 'RealTimeFlag={0}\n'.format(real_time_flag)

        metadata_threshold = kw.get('metadata_threshold', -1)
        put_directory_f += 'MetadataThreshold ={0}\n'.format(metadata_threshold)

        # We should do our job


        if not PosixPath(directory).exists():
                raise FileNotFoundError('directory not found: {0}'.format(directory))

        files = list(Path(directory).glob('*'))
        for index, file in enumerate(files):
            if Path(file).is_dir():
                raise Exception('{0} is a sub-folder'.format(file))

            put_directory_f += 'Files.{0}.Name={1}\n'.format(index, str(file.name))
            put_directory_f += 'Files.{0}.UploadFrom=disk\n'.format(index)
            put_directory_f += 'Files.{0}.Filename={1}\n'.format(index, file)
            put_directory_f += 'Files.{0}.Metadata.ContentType={1}\n'.format(index, magic.from_file(str(file), mime=True))

        put_directory_f += 'EndMessage\n'
        return put_directory_f.encode('utf-8'), identifier

    @staticmethod
    def put_complex_directory_redirect(**kw):
        ''' 
        ClientPutComplexDir\n
        URI=something\n
        Identifier=something\n
        Verbosity=0\n
        MaxRetries=10\n
        PriorityClass=1\n
        GetCHKOnly=false\n
        Global=false\n
        DontCompress=true\n
        ClientToken=Hello!!!\n
        LocalRequestOnly=false\n
        DefaultName=name\n
        Files.N.Name= name\n
        Files.N.UploadFrom=redirect\n
        Files.N.TargetURI=freenet uri\n
        EndMessage\n

        ##########

        arg:
        - node_identifier

        keywords:
        - uri
        - verbosity
        - max_retries
        - priority_class
        - get_chk_only
        - global_queue
        - codecs
        - dont_compress
        - client_token
        - persistence
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
        - target_uri_list: {name : 'Arnebab', uri : 'SSK@somehing', 'Linus' : 'CHK@something'}
        - site_name
        - default_name: Default index, e.g index.html if you set name 
                        of file that not exists in directory you are going to have an exception

        for more info https://github.com/freenet/wiki/wiki/FCPv2-ClientPutComplexDir
        Note: this function is used only from sending direct data, no file and no directory
        '''

        put_directory_r = 'ClientPutComplexDir\n'

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
                        'default_name' : {'type' : 'string', 'required': False} ,
                        'target_uri_list' : {'type' : 'list', 'required': True, 'empty': False} ,
                        'site_name' : {'type' : 'string', 'required': True, 'empty': False} ,
                    }

        v_succ = Validator(schema_succ)
        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        flag_default_name = False

        default_name = kw['default_name']

        target_uri_list = kw['target_uri_list']

        for uri in target_uri_list:
            if default_name == uri['name']:
                flag_default_name = True
                break

        if not flag_default_name:
            raise Exception('default_name must exist in URI list "target_uri_list"')

        site_name = kw['site_name']

        uri = kw.get('uri')

        put_directory_r += 'URI={0}\n'.format(uri)

        identifier = get_a_uuid()
        put_directory_r += 'Identifier={0}\n'.format(identifier)

        verbosity = kw.get('verbosity', 0)
        put_directory_r += 'Verbosity={0}\n'.format(verbosity)

        max_retries = kw.get('max_retries', -1)
        put_directory_r += 'MaxRetries={0}\n'.format(max_retries)

        priority_class = kw.get('priority_class', 2)
        put_directory_r += 'PriorityClass={0}\n'.format(priority_class)

        get_chk_only = kw.get('get_chk_only', False)
        put_directory_r += 'GetCHKOnly={0}\n'.format(get_chk_only)

        global_queue = kw.get('global_queue', False)
        put_directory_r += 'Global={0}\n'.format(global_queue)

        dont_compress = kw.get('dont_compress', False)
        put_directory_r += 'DontCompress={0}\n'.format(dont_compress)

        if not dont_compress:
            codecs = kw.get('codecs', None)
            if not codecs:
                codecs = 'list of codes'
                put_directory_r += 'Codecs={0}\n'.format(codecs)

        client_token = kw.get('client_token', None)
        if client_token != None:
            put_directory_r += 'ClientToken={0}\n'.format(client_token)

        persistence = kw.get('persistence', 'connection')

        if global_queue:
            persistence = 'forever'

        put_directory_r += 'Persistence={0}\n'.format(persistence)

        target_filename = kw.get('target_filename', None)
        if target_filename:
            put_directory_r += 'TargetFilename={0}\n'.format(target_filename)

        early_encode = kw.get('early_encode', False)
        put_directory_r += 'EarlyEncode={0}\n'.format(early_encode)

        binary_blob = kw.get('binary_blob', False)
        put_directory_r += 'BinaryBlob={0}\n'.format(binary_blob)

        fork_on_cacheable = kw.get('fork_on_cacheable', True)
        put_directory_r += 'ForkOnCacheable={0}\n'.format(fork_on_cacheable)

        extra_inserts_single_block = kw.get('extra_inserts_single_block', None)
        if extra_inserts_single_block != None:
            put_directory_r += 'ExtraInsertsSingleBlock ={0}\n'.format(extra_inserts_single_block)

        extra_inserts_splitfile_header_block = kw.get('extra_inserts_splitfile_header_block', None)
        if extra_inserts_splitfile_header_block != None:
            put_directory_r += 'ExtraInsertsSplitfileHeaderBlock={0}\n'.format(extra_inserts_single_block)

        compatibility_mode = kw.get('compatibility_mode', None)
        if compatibility_mode != None:
            put_directory_r += 'CompatibilityMode={0}\n'.format(compatibility_mode)

        local_request_only = kw.get('local_request_only', False)
        put_directory_r += 'LocalRequestOnly={0}\n'.format(local_request_only)

        override_splitfile_crypto_key = kw.get('override_splitfile_crypto_key', None)
        if override_splitfile_crypto_key != None:
            put_directory_r += 'OverrideSplitfileCryptoKey ={0}\n'.format(override_splitfile_crypto_key)

        real_time_flag = kw.get('real_time_flag', False)
        put_directory_r += 'RealTimeFlag={0}\n'.format(real_time_flag)

        metadata_threshold = kw.get('metadata_threshold', -1)
        put_directory_r += 'MetadataThreshold={0}\n'.format(metadata_threshold)

        # We should do our job

        for index, uri in enumerate(target_uri_list):
            put_directory_r += 'Files.{0}.Name={1}\n'.format(index, uri['name'])
            put_directory_r += 'Files.{0}.UploadFrom=redirect\n'.format(index)
            put_directory_r += 'Files.{0}.TargetURI={1}\n'.format(index, uri['uri'])

        put_directory_r += 'EndMessage\n'
        return put_directory_r.encode('utf-8'), identifier

    @staticmethod
    def put_complex_directory_data(**kw):
        ''' 
        ClientPutComplexDir\n
        URI=something\n
        Identifier=something\n
        Verbosity=0\n
        MaxRetries=10\n
        PriorityClass=1\n
        GetCHKOnly=false\n
        Global=false\n
        DontCompress=true\n
        ClientToken=Hello!!!\n
        LocalRequestOnly=false\n
        DefaultName=name\n
        Files.N.Name= name\n
        Files.N.UploadFrom=direct\n
        Files.N.DataLength=length_of_every_data\n
        EndMessage\n

        ##########

        keywords:
        - uri
        - verbosity
        - max_retries
        - priority_class
        - get_chk_only
        - global_queue
        - codecs
        - dont_compress
        - client_token
        - persistence
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
        - site_name
        - default_name: Default index, e.g index.html if you set name 
                        of file that not exists in directory you are going to have an exception

        for more info https://github.com/freenet/wiki/wiki/FCPv2-ClientPutComplexDir
        Note: this function is used only from sending direct data, no file and no directory
        '''

        put_directory_d = 'ClientPutComplexDir\n'

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
                        'default_name' : {'type' : 'string', 'required': False} ,
                        'site_name' : {'type' : 'string', 'required': True, 'empty': False} ,
                        'directory' : {'type' : 'string', 'required': True, 'empty': False} ,
                    }


        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        directory = kw['directory']
        default_name = kw['default_name']

        if not PosixPath(directory).exists():
                raise FileNotFoundError('directory not found: {0}'.format(directory))

        files = list(Path(directory).glob('*'))
        for index, file in enumerate(files):
            if Path(file).is_dir():
                raise Exception('{0} is a sub-folder'.format(file))

        if not PosixPath('{0}/{1}'.format(directory, default_name)).exists():
            raise FileNotFoundError('File not found: {0}'.format(default_name))

        site_name = kw['site_name']

        uri = kw.get('uri')

        put_directory_d += 'URI={0}\n'.format(uri)

        identifier = get_a_uuid()
        put_directory_d += 'Identifier={0}\n'.format(identifier)

        verbosity = kw.get('verbosity', 0)
        put_directory_d += 'Verbosity={0}\n'.format(verbosity)

        max_retries = kw.get('max_retries', -1)
        put_directory_d += 'MaxRetries={0}\n'.format(max_retries)

        priority_class = kw.get('priority_class', 2)
        put_directory_d += 'PriorityClass={0}\n'.format(priority_class)

        get_chk_only = kw.get('get_chk_only', False)
        put_directory_d += 'GetCHKOnly={0}\n'.format(get_chk_only)

        global_queue = kw.get('global_queue', False)
        put_directory_d += 'Global={0}\n'.format(global_queue)

        dont_compress = kw.get('dont_compress', False)
        put_directory_d += 'DontCompress={0}\n'.format(dont_compress)

        if not dont_compress:
            codecs = kw.get('codecs', None)
            if not codecs:
                codecs = 'list of codes'
                put_directory_d += 'Codecs={0}\n'.format(codecs)

        client_token = kw.get('client_token', None)
        if client_token != None:
            put_directory_d += 'ClientToken={0}\n'.format(client_token)

        persistence = kw.get('persistence', 'connection')

        if global_queue:
            persistence = 'forever'

        put_directory_d += 'Persistence={0}\n'.format(persistence)

        target_filename = kw.get('target_filename', None)
        if target_filename:
            put_directory_d += 'TargetFilename={0}\n'.format(target_filename)

        early_encode = kw.get('early_encode', False)
        put_directory_d += 'EarlyEncode={0}\n'.format(early_encode)

        binary_blob = kw.get('binary_blob', False)
        put_directory_d += 'BinaryBlob={0}\n'.format(binary_blob)

        fork_on_cacheable = kw.get('fork_on_cacheable', True)
        put_directory_d += 'ForkOnCacheable={0}\n'.format(fork_on_cacheable)

        extra_inserts_single_block = kw.get('extra_inserts_single_block', None)
        if extra_inserts_single_block != None:
            put_directory_d += 'ExtraInsertsSingleBlock ={0}\n'.format(extra_inserts_single_block)

        extra_inserts_splitfile_header_block = kw.get('extra_inserts_splitfile_header_block', None)
        if extra_inserts_splitfile_header_block != None:
            put_directory_d += 'ExtraInsertsSplitfileHeaderBlock={0}\n'.format(extra_inserts_single_block)

        compatibility_mode = kw.get('compatibility_mode', None)
        if compatibility_mode != None:
            put_directory_d += 'CompatibilityMode={0}\n'.format(compatibility_mode)

        local_request_only = kw.get('local_request_only', False)
        put_directory_d += 'LocalRequestOnly={0}\n'.format(local_request_only)

        override_splitfile_crypto_key = kw.get('override_splitfile_crypto_key', None)
        if override_splitfile_crypto_key != None:
            put_directory_d += 'OverrideSplitfileCryptoKey ={0}\n'.format(override_splitfile_crypto_key)

        real_time_flag = kw.get('real_time_flag', False)
        put_directory_d += 'RealTimeFlag={0}\n'.format(real_time_flag)

        metadata_threshold = kw.get('metadata_threshold', -1)
        put_directory_d += 'MetadataThreshold={0}\n'.format(metadata_threshold)

        # We should do our job
        files = list(Path(directory).glob('*'))
        data = []
        for index, file in enumerate(files):
            if Path(file).is_dir():
                raise Exception('{0} is a sub-folder'.format(file))
            
            f = open(str(file), 'rb').read()
            data.append(f)

            put_directory_d += 'Files.{0}.Name={1}\n'.format(index, str(file.name))
            put_directory_d += 'Files.{0}.UploadFrom=direct\n'.format(index)
            put_directory_d += 'Files.{0}.Filename={1}\n'.format(index, file)
            put_directory_d += 'Files.{0}.DataLength={1}\n'.format(index, str(file.stat().st_size))
            put_directory_d += 'Files.{0}.Metadata.ContentType={1}\n'.format(index, magic.from_file(str(file), mime=True))
            

        put_directory_d += 'Data\n'

        put_directory_d = put_directory_d.encode('utf-8')
        put_directory_d += b''.join(data)

        return put_directory_d, identifier

    
    @staticmethod
    def put_directory_disk(**kw):
        '''
        ClientPutDiskDir
        Identifier=My Identifier
        Verbosity=1023
        MaxRetries=999
        PriorityClass=2
        URI=CHK@
        GetCHKOnly=true
        DontCompress=true
        ClientToken=My Client Token
        Persistence=forever
        Global=true
        DefaultName=index.html
        Filename=/path/to/directory
        AllowUnreadableFiles=false // unless true, any unreadable files cause the whole request to fail; optional
        IncludeHiddenFiles=true // unless true, any "hidden" files will be ignored (from 1424)
        RealTimeFlag=false
        EndMessage
        
        keywords:
        - uri
        - verbosity
        - max_retries
        - priority_class
        - get_chk_only
        - global_queue
        - codecs
        - dont_compress
        - client_token
        - persistence
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

        - allow_unreadable_files 
        - include_hidden_files
        - ignore_usk_date_hints
        - write_to_client_cache 
        - override_splitfile_cryptokey
        
        - directory
        - site_name
        - default_name: Default index, e.g index.html if you set name 
                        of file that not exists in directory you are going to have an exception

        for more info https://github.com/freenet/wiki/wiki/FCPv2-ClientPutComplexDir
        Note: this function is used only from sending direct data, no file and no directory
        '''

        put_directory_dsk = 'ClientPutDiskDir\n'

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
                        'early_encode' : {'type' : 'boolean', 'required': False} ,
                        #'binary_blob' : {'type' : 'boolean', 'required': False} ,
                        'fork_on_cacheable' : {'type' : 'boolean', 'required': False} ,
                        'extra_inserts_single_block' : {'type' : 'integer', 'required': False, 'allowed': range(0, 10)} ,
                        'extra_inserts_splitfile_header_block' : {'type' : 'integer', 'required': False, 'allowed': range(0, 10)} ,
                        'compatibility_mode' : {'type' : 'string', 'required': False} ,
                        'local_request_only' : {'type' : 'boolean', 'required': False} ,
                        'override_splitfile_crypto_key' : {'type' : 'string', 'required': False} ,
                        'real_time_flag' : {'type' : 'boolean', 'required': False} ,

                        'allow_unreadable_files' : {'type' : 'boolean', 'required': False} ,
                        'include_hidden_files' : {'type' : 'boolean', 'required': False} ,
                        'ignore_usk_date_hints' : {'type' : 'boolean', 'required': False} ,
                        'write_to_client_cache' : {'type' : 'boolean', 'required': False} ,
                        'override_splitfile_cryptokey' : {'type' : 'string', 'required': False, 'empty': False} ,

                        'metadata_threshold' : {'type' : 'integer', 'required': False} ,
                        'default_name' : {'type' : 'string', 'required': False} ,
                        'site_name' : {'type' : 'string', 'required': True, 'empty': False} ,
                        'directory' : {'type' : 'string', 'required': True, 'empty': False} ,
                    }

        v_succ = Validator(schema_succ)
        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        directory = kw['directory']

        if not PosixPath(directory).exists():
                raise FileNotFoundError('directory not found: {0}'.format(directory))

        if kw.get('default_name', None):
            if not PosixPath('{0}/{1}'.format(directory, default_name)).exists():
                raise FileNotFoundError('File not found: {0}'.format(default_name))

            put_directory_dsk += 'DefaultName={0}\n'.format(default_name)

        uri = kw.get('uri')
        put_directory_dsk += 'URI={0}\n'.format(uri)

        site_name = kw['site_name']

        put_directory_dsk += 'Filename={0}\n'.format(directory)

        identifier = get_a_uuid()
        put_directory_dsk += 'Identifier={0}\n'.format(identifier)

        verbosity = kw.get('verbosity', 0)
        put_directory_dsk += 'Verbosity={0}\n'.format(verbosity)

        max_retries = kw.get('max_retries', -1)
        put_directory_dsk += 'MaxRetries={0}\n'.format(max_retries)

        priority_class = kw.get('priority_class', 2)
        put_directory_dsk += 'PriorityClass={0}\n'.format(priority_class)

        get_chk_only = kw.get('get_chk_only', False)
        put_directory_dsk += 'GetCHKOnly={0}\n'.format(get_chk_only)

        global_queue = kw.get('global_queue', False)
        put_directory_dsk += 'Global={0}\n'.format(global_queue)

        dont_compress = kw.get('dont_compress', False)
        put_directory_dsk += 'DontCompress={0}\n'.format(dont_compress)

        if not dont_compress:
            codecs = kw.get('codecs', None)
            if not codecs:
                codecs = 'list of codes'
                put_directory_dsk += 'Codecs={0}\n'.format(codecs)

        client_token = kw.get('client_token', None)
        if client_token != None:
            put_directory_dsk += 'ClientToken={0}\n'.format(client_token)

        persistence = kw.get('persistence', 'connection')

        if global_queue:
            persistence = 'forever'

        put_directory_dsk += 'Persistence={0}\n'.format(persistence)

        target_filename = kw.get('target_filename', None)
        if target_filename:
            put_directory_dsk += 'TargetFilename={0}\n'.format(target_filename)

        early_encode = kw.get('early_encode', False)
        put_directory_dsk += 'EarlyEncode={0}\n'.format(early_encode)

        #binary_blob = kw.get('binary_blob', False)
        #put_directory_dsk += 'BinaryBlob={0}\n'.format(binary_blob)

        fork_on_cacheable = kw.get('fork_on_cacheable', True)
        put_directory_dsk += 'ForkOnCacheable={0}\n'.format(fork_on_cacheable)

        extra_inserts_single_block = kw.get('extra_inserts_single_block', None)
        if extra_inserts_single_block != None:
            put_directory_dsk += 'ExtraInsertsSingleBlock ={0}\n'.format(extra_inserts_single_block)

        extra_inserts_splitfile_header_block = kw.get('extra_inserts_splitfile_header_block', None)
        if extra_inserts_splitfile_header_block != None:
            put_directory_dsk += 'ExtraInsertsSplitfileHeaderBlock={0}\n'.format(extra_inserts_single_block)

        compatibility_mode = kw.get('compatibility_mode', None)
        if compatibility_mode != None:
            put_directory_dsk += 'CompatibilityMode={0}\n'.format(compatibility_mode)

        local_request_only = kw.get('local_request_only', False)
        put_directory_dsk += 'LocalRequestOnly ={0}\n'.format(local_request_only)

        override_splitfile_crypto_key = kw.get('override_splitfile_crypto_key', None)
        if override_splitfile_crypto_key != None:
            put_directory_dsk += 'OverrideSplitfileCryptoKey ={0}\n'.format(override_splitfile_crypto_key)

        real_time_flag = kw.get('real_time_flag', False)
        put_directory_dsk += 'RealTimeFlag={0}\n'.format(real_time_flag)

        metadata_threshold = kw.get('metadata_threshold', -1)
        put_directory_dsk += 'MetadataThreshold ={0}\n'.format(metadata_threshold)

        allow_unreadable_files = kw.get('allow_unreadable_files', False)
        if allow_unreadable_files:
            put_directory_dsk += 'AllowUnreadableFiles={0}\n'.format(allow_unreadable_files)

        include_hidden_files = kw.get('include_hidden_files', False)
        if include_hidden_files:
            put_directory_dsk += 'includeHiddenFiles ={0}\n'.format(include_hidden_files)

        ignore_usk_date_hints = kw.get('ignore_usk_date_hints', False)
        if ignore_usk_date_hints:
            put_directory_dsk += 'IgnoreUSKDatehints ={0}\n'.format(ignore_usk_date_hints)

        write_to_client_cache = kw.get('write_to_client_cache', False)
        if override_splitfile_cryptokey:
            put_directory_dsk += 'WriteToClientCache ={0}\n'.format(write_to_client_cache)

        override_splitfile_cryptokey = kw.get('override_splitfile_cryptokey', None)
        if override_splitfile_cryptokey:
            paput_directory_dsk += 'OverrideSplitfileCryptoKey ={0}\n'.format(override_splitfile_cryptokey)

        # We should do our job

        put_directory_dsk += 'EndMessage\n'
        return put_directory_dsk.encode('utf-8'), identifier


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
    def get_stream(stream, **kw):
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
        - stream : must be a file object
        '''

        if not stream:
            raise Exception('stream must not be None')

        if not hasattr(stream, 'write'):
            raise Exception('stream must be a file object with attribute write e.g: stream = open(\'filename.extension\', \'ab\')')

        if not stream.mode == 'ab':
            raise Exception('stream must be "stream = open(\'filename.extension\', \'ab\')"')

        if stream.tell():
             raise Exception('File is not empty')

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
                        'initial_metadata_data_length' : {'type' : 'boolean', 'required': False} ,
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)
        

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
    def get_file(**kw):

        '''
        ClientGet\n
        IgnoreDS=false\n
        DSOnly=false\n
        URI=USK@something\n
        Identifier=Request Number One\n
        Verbosity=0\n
        ReturnType=disk\n
        MaxSize=100\n
        MaxTempSize=1000\n
        MaxRetries=100\n
        PriorityClass=1\n
        Persistence=forever\n
        ClientToken=hello\n
        Filename=something\n
        TempFilename=something\n
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
        - filename
        - temp_filename
        '''

        get_f = 'ClientGet\n'

        schema_succ =   {

                        'uri': {'type' : 'string', 'required': True, 'empty': False },
                        'ds_only' : {'type' : 'boolean', 'required': False } ,
                        'verbosity' : {'type' : 'integer' , 'required': False}  ,
                        'ignore_ds' : {'type' : 'boolean', 'required': False } ,
                        'priority_class' : {'type' : 'integer', 'allowed': [0, 1, 2, 3, 4, 5, 6], 'required': False } ,
                        'max_size' : {'type' : 'integer', 'required': False } ,
                        'global_queue' : {'type' : 'boolean' , 'required': False } ,
                        'max_temp_size' : {'type' : 'integer', 'required': False } ,
                        'max_retries' : {'type' : 'integer', 'required': False } ,
                        'client_token' : {'type' : 'string', 'required': False } ,
                        'persistence' : {'type' : 'string','allowed': ['connection','forever','reboot'], 'required': False } ,
                        'binary_blob' : {'type' : 'boolean', 'required': False } ,
                        'filter_data' : {'type' : 'boolean', 'required': False } ,
                        'initial_metadata_data_length' : {'type' : 'boolean', 'required': False } ,
                        'filename' : {'type' : 'string', 'required': True, 'empty' : False } ,
                        'temp_filename' : {'type' : 'string', 'required': False } , 
                    }

        v_succ = Validator(schema_succ)

        if not v_succ.validate(kw):
            raise Exception(v_succ.errors)

        identifier = get_a_uuid()

        ignore_ds = kw.get('ignore_ds', False)
        get_f += 'IgnoreDS={}\n'.format(ignore_ds)

        ds_only = kw.get('ds_only', False)
        get_f += 'DSOnly={}\n'.format(ds_only)

        uri = kw['uri']
        get_f += 'URI={}\n'.format(uri)

        global_queue = kw.get('global_queue', False)
        get_f += 'Global={}\n'.format(global_queue)

        get_f += 'Identifier={}\n'.format(identifier)

        persistent = kw.get('persistent', 'connection')

        if global_queue:
            persistent = 'forever'

        get_f += 'Persistence={}\n'.format(persistent)

        priority_class = kw.get('priority_class', 2)
        get_f += 'PriorityClass={}\n'.format(priority_class)

        get_f += 'ReturnType=disk\n'

        filter_data = kw.get('filter_data', False)
        get_f += 'FilterData=false\n'

        filename = kw['filename']
        get_f += f'Filename={filename}\n'

        temp_filename = kw.get('temp_filename', None)
        if temp_filename:
            get_f += f'TempFilename={temp_filename}\n'

        get_f += 'EndMessage\n'

        return get_f.encode('utf-8'), identifier 

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
        
        schema_succ = {
                       'header': {'type' : 'string', 'required' : True, 'empty': False ,'allowed': ['NodeHello']},
                       'CompressionCodecs' : {'type' : 'string'} ,
                       'Revision' : {'type' : 'string'} ,
                       'Testnet' : {'type' : 'string'} ,
                       'Version' : {'type' : 'string'} ,
                       'Build' : {'type' : 'string'} ,
                       'ConnectionIdentifier' : {'type' : 'string', 'required' : True, 'empty': False} ,
                       'Node' : {'type' : 'string'} ,
                       'ExtBuild' : {'type' : 'string'} ,
                       'FCPVersion' : {'type' : 'string'} ,
                       'NodeLanguage' : {'type' : 'string'} ,
                       'ExtRevision' : {'type' : 'string'} ,
                       'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return 'Connection started'

        return False

    @staticmethod
    def close_connection_duplicate_client_name(data):
        '''
        {'header' : 'CloseConnectionDuplicateClientName',
        'footer' : 'EndMessage'}
        '''
        
        schema_succ = {
                   'header': {'type' : 'string', 'required' : True, 'allowed': ['CloseConnectionDuplicateClientName']},
                   'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return True

        return False


    @staticmethod
    def identifier_collision(data):
        '''
        {'header': 'IdentifierCollision', 'Identifier': 'None', 'Global': 'true', 'footer': 'EndMessage'}
        '''
        schema_succ = {
                   'header': {'type' : 'string', 'allowed': ['IdentifierCollision']},
                   'Identifier' : {'type' : 'string', 'required' : False} ,
                   'Global' : {'type' : 'string', 'required': False} ,
                   'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return True

        return False

    # __Begin__ ProtocolError

    @staticmethod
    def protocol_error(data):
        '''
        {'header': 'ProtocolError', 'Identifier': 'IHwY2ROpRfaxxj5ocVC9LgIHwY2ROpRfaxxj5ocVC9LgIHwY2ROpRfaxxj5ocVC9Lg', 
        'CodeDescription': 'Error parsing freenet URI', 'Fatal': 'false', 'Code': '4', 'ExtraDescription': 
        'There is no @ in that URI! (pub)', 'Global': 'true', 'footer': 'EndMessage'}
        '''
        schema_succ = {
                   'header': {'type' : 'string', 'allowed': ['ProtocolError']},
                   'Identifier' : {'type' : 'string', 'required' : False} ,
                   'Fatal' : {'type' : 'string', 'required' : False} ,
                   'Code' : {'type' : 'string', 'required' :False} ,
                   'Global' : {'type' : 'string', 'required': False} ,
                   'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return True

        return False
    # __End__ ProtocolError

    @staticmethod
    def get_failed(data):
        '''
        {'header': 'GetFailed', 'Identifier': 'zaXGDmApTB6vRLOYN_3_WwzaXGDmApTB6vRLOYN_3_WwzaXGDmApTB6vRLOYN_3_Ww', 
        'CodeDescription': 'Permanent redirect: use the new URI', 'ShortCodeDescription': 'New URI', 
        'RedirectURI': 'USK@uonktR0ZSTIlBWiK5o4Uf0yzDKUNuDuHSDzvUZYCgU0,cMUguHw0DwkU04Uxx5grg5XSVw~Z4cRbF4aAY6MUbNQ,AQACAAE/redirect/3',
         'Fatal': 'true', 'Code': '27', 'footer': 'EndMessage'}
        '''
        schema_succ = {
                   'header': {'type' : 'string', 'allowed': ['GetFailed']},
                   'Identifier' : {'type' : 'string', 'required' : True} ,
                   'CodeDescription' : {'type' : 'string', 'required' : False} ,
                   'ShortCodeDescription' : {'type' : 'string', 'required' : False} ,
                   'RedirectURI' : {'type' : 'string', 'required': False} ,
                   'Errors' : {'type' : 'string', 'required': False} ,
                   'ExpectedDataLength' : {'type' : 'string', 'required': False} ,
                   'ExpectedMetadata.ContentType' : {'type' : 'string', 'required': False} ,
                   'FinalizedExpected' : {'type' : 'string', 'required': False} ,
                   'Fatal' : {'type' : 'string', 'required': False} ,
                   'Code' : {'type' : 'string', 'required': False} ,
                   'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    # __Begin__ WatchGlobal

    @staticmethod
    def generate_keys(uri_type, name, data):
        '''
        data received from Node after parsing:

        { 'header' : 'SSKKeypair', 'InsertURI' : 'SSK@something', 
        'RequestURI' : ,'Identifier' : 'SSK@Bsomething', 'footer' : 'EndMessage' }
        '''

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
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            private_key = data['InsertURI']
            public_key = data['RequestURI']
            identifier = data['Identifier']

            if uri_type == 'SSK':
                if name:
                    public_key = '{0}{1}'.format(data['RequestURI'], name)
                    private_key = '{0}{1}'.format(data['InsertURI'], name)
                else :
                    public_key = '{0}'.format(data['RequestURI'])
                    private_key = '{0}'.format(data['InsertURI'])

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
                    ksk = 'KSK@{0}-{1}'.format(get_a_uuid(5), name)
                    return identifier, ksk

                ksk = 'KSK@{0}'.format(get_a_uuid(5))
                return identifier, ksk

            return identifier, (public_key, private_key)

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
                        'header': {'type' : 'string',  'required' : True, 'empty': False, 'allowed': ['TestDDAReply']},
                        'Directory' : {'type' : 'string'} ,
                        'ReadFilename' : {'type' : 'string'} ,
                        'WriteFilename' : {'type' : 'string'} ,
                        'ContentToWrite' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data

        return False

    @staticmethod
    def test_dda_complete(data):
        '''
         {'header': 'TestDDAComplete', 'ReadDirectoryAllowed': 'true', 
         'Directory': '/usr/home/jamesaxl/Music/site_test', 'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['TestDDAComplete']} ,
                        'Directory' : {'type' : 'string' , 'required' : True, 'empty': False} ,
                        'ReadDirectoryAllowed' : {'type' : 'string' ,'required' : False, 'empty': False} ,
                        'WriteDirectoryAllowed' : {'type' : 'string' ,'required' : False, 'empty': False} ,
                        'ContentToWrite' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
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

         {'header': 'PersistentGet', 'MaxRetries': '0', 'Started': 'false', 'PriorityClass': '2', 
         'Filename': '/usr/home/jamesaxl/Freenet/downloads/thing.ogg', 'Verbosity': '2147483647', 
         'ReturnType': 'disk', 
         'URI': 'CHK@yebutzYYDIXbZ1SoIzynbjMy0IadBTshfXpDp22K0pA,BwXjATt750cekkxDSIG75iVFM8FVpNGNAcJRRKURHpE,AAMC--8/metal.ogg', 
         'MaxSize': '9223372036854775807', 'Global': 'true', 'Persistence': 'forever', 'BinaryBlob': 
         'false', 'Identifier': 'JlMhQDLNTeWsVkK2Vlu8DQ', 'RealTime': 'false', 'footer': 'EndMessage'}
        '''

        schema_succ = {
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['PersistentGet']},
                        'MaxRetries' : {'type' : 'string'} ,
                        'Started' : {'type' : 'string'} ,
                        'PriorityClass' : {'type' : 'string'} ,
                        'Filename' : {'type' : 'string', 'required' : False} ,
                        'BinaryBlob' : {'type' : 'string'} ,
                        'Verbosity' : {'type' : 'string'} ,
                        'URI' : {'type' : 'string'} ,
                        'Persistence' : {'type' : 'string'} ,
                        'RealTime' : {'type' : 'string'} ,
                        'MaxSize' : {'type' : 'string'} ,
                        'ReturnType': {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
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
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['DataFound']},
                        'CompletionTime' : {'type' : 'string'} ,
                        'StartupTime' : {'type' : 'string'} ,
                        'DataLength' : {'type' : 'string'} ,
                        'Metadata.ContentType' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
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
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['PersistentPut']},
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
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def started_compression(data):
        '''

        { 'header': 'StartedCompression', 'Codec': 'GZIP', 
          'Identifier': '-yfOweULTUqRSXBah8zNSA-yfOweULTUqRSXBah8zNSA-yfOweULTUqRSXBah8zNSA', 
          'Global': 'true', 'footer': 'EndMessage' }

        '''

        schema_succ = {
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['StartedCompression']},
                        'Codec' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
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
                        'header': {'type' : 'string',  'required' : True, 'empty': False, 'allowed': ['FinishedCompression']},
                        'Codec' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'CompressedSize' : {'type' : 'string'} ,
                        'OriginalSize' : {'type' : 'string'} ,
                        'Codec.Name' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
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
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['SimpleProgress']},
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
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def sending_to_network(data):
        '''
        {'header': 'SendingToNetwork', 
        'Identifier': 'YN_fi4KIQvyVA_Kg2XDNrgYN_fi4KIQvyVA_Kg2XDNrgYN_fi4KIQvyVA_Kg2XDNrg', 
        'Global': 'true', 'footer': 'EndMessage'}
        '''
        
        schema_succ = {
                        'header': {'type' : 'string', 'required' : True, 'empty' : False, 'allowed': ['SendingToNetwork']},
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def expected_hashes(data):
        '''
        {'header': 'ExpectedHashes', 'Identifier': 'YN_fi4KIQvyVA_Kg2XDNrgYN_fi4KIQvyVA_Kg2XDNrgYN_fi4KIQvyVA_Kg2XDNrg',
         'Global': 'true', 'Hashes.SHA256': 'ce0b2ed50716daa00d07ed4599c3f39e556b453ef07c9692cfeb19d63b9a9538', 
         'Hashes.SHA1': 'b3a341235e68c020c3fc2d3f76fde5be7c2ce96f', 'Hashes.MD5': 'c744d4a17230f1354330f0e0ea59817a', 
         'footer': 'EndMessage'}

        OR
        
        {'header': 'ExpectedHashes', 'Identifier': 'something', 
        'Global': 'true', 'Hashes.SHA256': 'something', 
        'footer': 'EndMessage'}

        '''
        
        schema_succ = {
                        'header': {'type' : 'string', 'required' : True, 'empty' : False, 'allowed': ['ExpectedHashes']},
                        'Identifier' : {'type' : 'string'} ,
                        'Hashes.SHA256' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'Hashes.SHA1' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'Hashes.MD5' : {'type' : 'string', 'required' : False, 'empty' : False,} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def compatibility_mode(data):
        '''
        {'header': 'CompatibilityMode', 'Min': 'COMPAT_1416', 
        'Identifier': 'DmLQYj52RBCBohafwM0xCgDmLQYj52RBCBohafwM0xCgDmLQYj52RBCBohafwM0xCg', 
        'Max': 'COMPAT_1468', 'Definitive': 'true', 
        'SplitfileCryptoKey': '21a4e353ae0cc09b7b179df91b47f78e1ce47018bfeeacb51d254a7bf475dbb2', 
        'Global': 'true', 'DontCompress': 'true', 'Min.Number': '6', 'Max.Number': '7', 'footer': 'EndMessage'}

        '''
        
        schema_succ = {
                        'header': {'type' : 'string', 'required' : True, 'empty' : False, 'allowed': ['CompatibilityMode']},
                        'Identifier' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'Max' : {'type' : 'string' , 'required' : False, 'empty' : False} ,
                        'Min' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'Definitive' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'DontCompress' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'SplitfileCryptoKey' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'Min.Number' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'Max.Number' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'Global' : {'type' : 'string', 'required' : False, 'empty' : False} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def expected_mime(data):
        '''
         { 'header': 'ExpectedMIME', 'Identifier': 'YfoPgI_vRT6zqlaSeHbUdAYfoPgI_vRT6zqlaSeHbUdAYfoPgI_vRT6zqlaSeHbUdA', 
         'Global': 'true', 'Metadata.ContentType': 'audio/ogg', 'footer': 'EndMessage' }
        '''
        
        schema_succ = {
                        'header': {'type' : 'string', 'required' : True, 'empty' : False, 'allowed': ['ExpectedMIME']},
                        'Identifier' : {'type' : 'string'} ,
                        'Metadata.ContentType' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def expected_data_length(data):
        '''
        {'header': 'ExpectedDataLength', 'Identifier': 'YN_fi4KIQvyVA_Kg2XDNrgYN_fi4KIQvyVA_Kg2XDNrgYN_fi4KIQvyVA_Kg2XDNrg', 
        'DataLength': '0', 'Global': 'true', 'footer': 'EndMessage'}

        '''
        
        schema_succ = {
                        'header': {'type' : 'string', 'required' : True, 'empty' : False, 'allowed': ['ExpectedDataLength']},
                        'Identifier' : {'type' : 'string'} ,
                        'DataLength' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string', } ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

    @staticmethod
    def persistent_request_removed(data):
        '''
        {'header': 'PersistentRequestRemoved', 'Identifier': 'PfdChTyLRHC7JzzKZCuDeQPfdChTyLRHC7JzzKZCuDeQPfdChTyLRHC7JzzKZCuDeQ', 
        'Global': 'true', 'footer': 'EndMessage'}
        '''
        
        schema_succ = {
                        'header': {'type' : 'string', 'required' : True, 'empty' : False, 'allowed': ['PersistentRequestRemoved']},
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string', 'required' : True, 'empty' : False} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']
 
        raise Exception(v_succ.errors)

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
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
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
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['PutFetchable']},
                        'URI' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
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
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['PutSuccessful']},
                        'URI' : {'type' : 'string'} ,
                        'Identifier' : {'type' : 'string'} ,
                        'CompletionTime' : {'type' : 'string'} ,
                        'StartupTime' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
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
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['PutFailed']},
                        'Identifier' : {'type' : 'string'} ,
                        'CodeDescription' : {'type' : 'string'} ,
                        'ShortCodeDescription' : {'type' : 'string'} ,
                        'Fatal' : {'type' : 'string'} ,
                        'Code' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
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
                        'header': {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['PersistentRequestRemoved']},
                        'Identifier' : {'type' : 'string'} ,
                        'Global' : {'type' : 'string'} ,
                        'footer' : {'type' : 'string', 'required' : True, 'empty': False, 'allowed': ['EndMessage']}
                      }

        v_succ = Validator(schema_succ)

        if v_succ.validate(data):
            return data['Identifier']

        return False

# Do not Touch this function if you can not make something better
# Its nickname is Barnamy
def barnamy_parsing_received_request_in_bytes(data):

    data = data.decode('utf-8').split('\n')
    data_list = []
    data_dic = {}

    for item in data:
        if len(item.split('=')) == 1:
            if item == 'EndMessage':
                data_dic['footer'] = item
                if data_dic not in data_list:
                    data_list.append(data_dic)
                data_dic = {}
            else :
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
def get_a_uuid(round = 3):
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    key = ''
    for i in range(round):
        key += r_uuid.decode().replace('=', '')
    
    return key

def check_freenet_key(uri):
    # We should ask Arnebab after
    pass
