# -*- coding: utf-8 -*-

'''
FCP API in Python created by James Axl 2018

For FCP documentation, see http://wiki.freenetproject.org/FCPv2 still under construction
'''

import os
import sqlite3
from sqlite3 import Error
from datetime import datetime
from abc import ABCMeta, abstractmethod
from pathlib import Path
from .Logger import LOGGER
from .Core import DB_FILENAME

DB_SCHEMA = '''
CREATE TABLE IF NOT EXISTS radio (
    identifier              TEXT PRIMARY KEY NOT NULL,
    name                    TEXT UNIQUE NOT NULL,
    path                    TEXT NOT NULL,
    size                    TEXT NOT NULL,
    prv                     TEXT UNIQUE NOT NULL,
    pub                     TEXT UNIQUE NOT NULL,
    is_uploaded             INTEGER DEFAULT 0,
    description             TEXT NOT NULL DEFAULT 'N/A',
    version                 INTEGER NOT NULL DEFAULT 0,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS track (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name                    TEXT NOT NULL,
    metadata_content_type   TEXT NOT NULL,
    size                    INTEGER NOT NULL,
    chk                     TEXT NOT NULL,
    version                 INTEGER NOT NULL DEFAULT 0,
    is_uploaded             INTEGER DEFAULT 0,
    radio_id                INTEGER NOT NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(radio_id) REFERENCES radio(identifier) ON DELETE CASCADE ON UPDATE CASCADE
);

'''


def init_db_con():
    con = None
    try:
        if not Path(DB_FILENAME).exists():
            con = sqlite3.connect(DB_FILENAME, check_same_thread=False)
            con.executescript(DB_SCHEMA)
            LOGGER.info('RADIO DATABASE HAS BEEN CREATED')
        else:
            con = sqlite3.connect(DB_FILENAME, check_same_thread=False)
    except Error as e:
        print(e)
    return con

class BaseModel(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def insert(self): raise NotImplementedError
    
    @abstractmethod
    def update(self): raise NotImplementedError
    
    @abstractmethod
    def update_upload(self): raise NotImplementedError

    @abstractmethod
    def delete(self): raise NotImplementedError
    
    @abstractmethod
    def select(self): raise NotImplementedError

    @abstractmethod
    def select_all(self): raise NotImplementedError
    
    

class RadioModel(BaseModel):
    
    def __init__(self, con):
        self.db_con = con
    
    def insert(self, 
               identifier, 
               name, 
               path_dir, 
               prv, 
               pub, 
               version):

        dir_size = sum(f.stat().st_size for f in Path(path_dir).glob('**/*') if f.is_file() )
        
        self.db_con.execute('''
                   INSERT INTO radio 
                   (identifier, name, path, size, prv, pub, version)
                   VALUES (?, ?, ?, ?, ?, ?, ?);''', ( identifier, name, 
                                                       path_dir, dir_size,
                                                       prv, pub, version ))
        self.db_con.commit()
    
    def update_upload(self, identifier): 
        sql = ''' UPDATE radio SET is_uploaded = 1 WHERE identifier = ? ; '''                    
        cursor = self.db_con.cursor()
        cursor.execute(sql, (identifier,) )
        self.db_con.commit()
    
    def update(self, 
               path_dir, 
               prv, 
               pub, 
               version, 
               name):

        updated_at = datetime.today().strftime('%Y-%m-%d')
        self.db_con.execute('''
                                UPDATE radio 
                                SET path = ?
                                , prv = ?
                                , pub = ?
                                , version = ?
                                , size = ?
                                , updated_at = ?
                                WHERE
                                name = ?;''', ( path_dir, 
                                                prv, 
                                                pub, 
                                                version, 
                                                os.stat(path_dir).st_size,
                                                updated_at, 
                                                name ),)

        self.db_con.commit()
    
    def select_all(self, page): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM radio LIMIT 10 OFFSET ?; ''', ((page - 1) * 10,))
        cursor_r = cursor.fetchall()
        return cursor_r
    
    def delete(self, name_of_site): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' DELETE radio WHERE name = ?; ''', (name_of_site,))
        cursor_r = cursor.fetchone()
        self.db_con.commit()
        LOGGER.info('{0} HAS BEEN DELETED'.format(name_of_site))
        return cursor_r
    
    def check_if_radio_exist(self, name_of_site):
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM radio WHERE name = ?; ''', (name_of_site,))
        cursor_r = cursor.fetchone()
        self.db_con.commit()
        return cursor_r

    def check_if_radio_uploaded(self, name_of_site):
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM radio WHERE name = ? AND is_uploaded = 1; ''', (name_of_site,))
        cursor_r = cursor.fetchone()
        self.db_con.commit()
        return cursor_r

class TrackModel(BaseModel):

    def __init__(self, con):
        self.db_con = con

    def insert(self, name, 
                     metadata_content_type, 
                     size,
                     uri,
                     identifier): 

        self.db_con.execute('''
            INSERT INTO track ( name, metadata_content_type, 
            size, chk, radio_id )
            VALUES (?, ?, ?, ?, ?);''', ( name, 
                                          metadata_content_type, 
                                          size,
                                          uri,
                                          identifier, ))
        self.db_con.commit()

    def update_upload(self, chk):
        sql = ''' UPDATE track SET is_uploaded = 1 WHERE chk = ? ; '''
        cur = self.db_con.cursor()
        self.db_con.execute(sql, (chk,))
        self.db_con.commit()

    def check_if_chk_exist(self, chk, identifier):
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM track 
                           WHERE chk = ? 
                           AND radio_id = ? ; ''', (chk, identifier,))

        cursor_r = cursor.fetchone()
        self.db_con.commit()
        return cursor_r

    def select_belong_to_radio(self, radio_id): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM track
                           WHERE radio_id = ? ; ''', (radio_id,))

        cursor_r = cursor.fetchall()
        self.db_con.commit()
        return cursor_r

    def delete(self, _file, radio_id): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' DELETE FROM track WHERE name = ? AND radio_id = ?; ''', (_file, radio_id))
        self.db_con.commit()
        LOGGER.info('TRACK HAS BEEN DELETED')
