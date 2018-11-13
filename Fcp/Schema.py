# encoding: utf-8

try:
    from cerberus import Validator
except ModuleNotFoundError:
    raise ModuleNotFoundError('cerberus module is required')

import uuid
import base64

# __Begin__ ClientHello
def client_hello_send(**kw):
    '''
    ClientHello
    Name=My Freenet Client
    ExpectedVersion=2.0
    EndMessage
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

def client_hello_receive(data):
    
    '''
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

    schema_err = {
                   'header': {'type' : 'string', 'allowed': ['CloseConnectionDuplicateClientName', 'ProtocolError']},
                   'footer' : {'type' : 'string'}
                 }

    v_succ = Validator(schema_succ)

    v_err = Validator(schema_err)
    
    if v_succ.validate(parsing_data_generator):
        return 'Connection started'
    elif v_err.validate(parsing_data_generator):
        if parsing_data_generator['header'] == 'CloseConnectionDuplicateClientName':
            return 'you have a connection with same name'
        elif parsing_data_generator['header'] == 'ProtocolError':
            return 'ClientHello must be first message'

    return False
# __End__ ClientHello

# __Begin__ ErrorLogin
def error_login_receive(data):
    schema_err = {
               'header': {'type' : 'string', 'allowed': ['CloseConnectionDuplicateClientName', 'ProtocolError']},
               'footer' : {'type' : 'string'}
             }

    v_err = Validator(schema_err)

    v_err = Validator(schema_err)
    
    if v_err.validate(parsing_data_generator):
        if parsing_data_generator['header'] == 'CloseConnectionDuplicateClientName':
            return 'you have a connection with same name'
        elif parsing_data_generator['header'] == 'ProtocolError':
            return 'ClientHello must be first message'

    return False
# __End__ErrorLogin

# __Begin__ WatchGlobal
def watch_global_send():
    watch_global = 'WatchGlobal\n'
    watch_global += 'nIdentifier=__global\n'
    watch_global += 'EndMessage\n'

    return watch_global.encode('utf-8')
# __End__ WatchGlobal

# __Begin__ GenerateSSK
def generate_keys_send():

    identifier = get_a_uuid()

    genrate_key = 'GenerateSSK\n'
    genrate_key += 'Identifier={0}\n'.format(identifier)
    genrate_key += 'EndMessage\n'

    return genrate_key.encode('utf-8'), identifier
 
def generate_keys_receive(uri_type, name, data):
    '''
    SSKKeypair
    InsertURI=freenet:SSK@something/
    RequestURI=freenet:SSK@Bsomething/
    Identifier=something
    EndMessage
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


def disconnect_send(**kw):
    '''
    Disconnect
    EndMessage
    '''
    disconnect = 'Disconnect\n'
    disconnect += 'EndMessage\n'
    return disconnect.encode('utf-8')

def put_data_send(**kw):
    
    put_data = 'ClientPut\n'

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
    put_data += 'URI={0}\n'.format(uri)
    
    metadata_content_type = kw.get('metadata_content_type', 'application/octet-stream')
    put_data += 'Metadata.ContentType={0}\n'.format(metadata_content_type)

    identifier = get_a_uuid()
    put_data += 'Identifier={0}\n'.format(identifier)

    verbosity = kw.get('verbosity', 0)
    put_data += 'Verbosity={0}\n'.format(verbosity)

    max_retries = kw.get('max_retries', -1)
    put_data += 'MaxRetries={0}\n'.format(max_retries)
    
    priority_class = kw.get('priority_class', 2)
    put_data += 'PriorityClass={0}\n'.format(priority_class)
    
    get_chk_only = kw.get('get_chk_only', False)
    put_data += 'GetCHKOnly={0}\n'.format(get_chk_only)
    
    global_queue = kw.get('global_queue', False)
    put_data += 'Global={0}\n'.format(global_queue)
    
    dont_compress = kw.get('dont_compress', False)
    put_data += 'DontCompress={0}\n'.format(dont_compress)
    
    codecs = kw.get('codecs', None)
    
    client_token = kw.get('client_token', None)
    if client_token != None:
        put_data += 'ClientToken={0}\n'.format(client_token)
    
    if global_queue:
        persistence = 'forever'

    persistence = kw.get('persistence', 'connection')
    put_data += 'Persistence={0}\n'.format(persistence)
    
    target_filename = kw.get('target_filename', None)
    
    early_encode = kw.get('early_encode', False)
    put_data += 'EarlyEncode={0}\n'.format(early_encode)

    upload_from = 'direct'
    put_data += 'UploadFrom={0}\n'.format(upload_from)
    
    binary_blob = kw.get('binary_blob', False)
    put_data += 'BinaryBlob={0}\n'.format(binary_blob)

    fork_on_cacheable = kw.get('fork_on_cacheable', True)
    put_data += 'ForkOnCacheable={0}\n'.format(fork_on_cacheable)

    extra_inserts_single_block = kw.get('extra_inserts_single_block', None)
    if extra_inserts_single_block != None:
        put_data += 'ExtraInsertsSingleBlock ={0}\n'.format(extra_inserts_single_block)

    extra_inserts_splitfile_header_block = kw.get('extra_inserts_splitfile_header_block', None)
    if extra_inserts_splitfile_header_block != None:
        put_data += 'ExtraInsertsSplitfileHeaderBlock={0}\n'.format(extra_inserts_single_block)

    compatibility_mode = kw.get('compatibility_mode', None)
    if compatibility_mode != None:
        put_data += 'CompatibilityMode={0}\n'.format(compatibility_mode)

    local_request_only = kw.get('local_request_only', False)
    put_data += 'LocalRequestOnly ={0}\n'.format(local_request_only)

    override_splitfile_crypto_key = kw.get('override_splitfile_crypto_key', None)
    if override_splitfile_crypto_key != None:
        put_data += 'OverrideSplitfileCryptoKey ={0}\n'.format(override_splitfile_crypto_key)
    
    real_time_flag = kw.get('real_time_flag', False)
    put_data += 'RealTimeFlag={0}\n'.format(real_time_flag)

    metadata_threshold = kw.get('metadata_threshold', -1)
    put_data += 'MetadataThreshold ={0}\n'.format(metadata_threshold)

    if global_queue:
        persistence = 'forever'

    data = kw.get('data')
    data_length = len(data.encode('utf-8'))
    put_data += 'DataLength={0}\n'.format(data_length)
    put_data += 'Data\n{0}\n'.format(data)

    return put_data.encode('utf-8'), identifier

def put_file_send(self):
    pass

def put_redirect_send(self):
    pass

def put_directory_send(self):
    ''' 
    '''
    pass

def get_data_send(**kw):
    
    '''
    ClientGet
    IgnoreDS=false
    DSOnly=false
    URI=USK@something
    Identifier=Request Number One
    Verbosity=0
    ReturnType=direct
    MaxSize=100
    MaxTempSize=1000
    MaxRetries=100
    PriorityClass=1
    Persistence=reboot
    ClientToken=hello
    Global=false
    BinaryBlob=false
    FilterData=true
    EndMessage
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

def get_request_status_send(identifier):
    '''
    GetRequestStatus
    Identifier=something
    Persistence=forever
    Global=true
    EndMessage
    '''

    get_request_status =  'GetRequestStatus\n'
    get_request_status += 'Identifier={0}\n'.format(identifier)
    get_request_status += 'Persistence=forever\n'
    get_request_status += 'Global=true\n'
    get_request_status += 'EndMessage\n'

    return get_request_status.encode('utf-8')

def persistent_get(data):
    '''
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

def data_found(data):
    '''
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

def all_data(data):
    '''
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

def remove_data_send(identifier):
    '''
    RemovePersistentRequest
    Global=true,
    Identifier=somethimg
    '''
    remove_data = 'RemovePersistentRequest\n'
    remove_data += 'Identifier={0}\n'.format(identifier)
    remove_data += 'Global=true\n'
    remove_data += 'EndMessage\n'

    return remove_data.encode('utf-8')

def put_data_receive(data, identifier):
    parsing_data_generator = parsing_data(data)

    for item in parsing_data_generator:
        if item.get('Identifier', None) == identifier:
            yield item


def persistent_put(data):
    '''
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

def expected_hashes(data):
    '''
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

def finished_compression(data):
    '''
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

def simple_progress(data):
    '''
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

def uri_generated(data):
    '''
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


def put_fetchable(data):
    '''
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

def put_successful(data):
    '''
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

def put_failed(data):
    '''
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

def persistent_request_removed(data):
    '''
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
def parsing_data(data):
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
                data_list.append(data_dic)
                data_dic = {}
            elif item == 'Data':
                iam_data = True 
            else:
                data_dic['header'] = item
        elif len(item.split('=')) == 2:
            data_dic[item.split('=')[0]] = item.split('=')[1]

    return data_list

# Avoid collision. still under test though. I will try to make identify more complex
# We should Ask Arnebab Again
def get_a_uuid():
    r_uuid = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    return r_uuid.decode().replace('=', '')

def check_freenet_key(uri):
    # We should ask Arnebab after
    pass