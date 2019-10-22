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
CREATE TABLE IF NOT EXISTS website (
    identifier              TEXT PRIMARY KEY NOT NULL,
    name                    TEXT UNIQUE NOT NULL,
    default_index           TEXT NOT NULL,
    path                    TEXT NOT NULL,
    size                    TEXT NOT NULL,
    prv                     TEXT UNIQUE NOT NULL,
    pub                     TEXT UNIQUE NOT NULL,
    is_uploaded             INTEGER DEFAULT 0,
    description             TEXT NOT NULL DEFAULT 'N/A',
    version                 INTEGER NOT NULL DEFAULT 0,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP
);

CREATE TABLE IF NOT EXISTS file_manifest (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name                    TEXT NOT NULL,
    metadata_content_type   TEXT NOT NULL,
    size                    INTEGER NOT NULL,
    prv                     TEXT UNIQUE NOT NULL,
    pub                     TEXT UNIQUE NOT NULL,
    is_uploaded             INTEGER DEFAULT 0,
    website_id              INTEGER NOT NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP,
    FOREIGN KEY(website_id) REFERENCES website(identifier) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS file_separate (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name                    TEXT NOT NULL,
    metadata_content_type   TEXT NOT NULL,
    size                    INTEGER NOT NULL,
    chk                     TEXT NOT NULL,
    is_uploaded             INTEGER DEFAULT 0,
    website_id              INTEGER NOT NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP,
    FOREIGN KEY(website_id) REFERENCES website(identifier) ON DELETE CASCADE ON UPDATE CASCADE
);
'''


def init_db_con():
    con = None
    try:
        con = sqlite3.connect(DB_FILENAME, check_same_thread=False)
    except Error as e:
        print(e)
    return con

def init_db(con):
    con.executescript(DB_SCHEMA)
    LOGGER.info('WEBSITE DATABASE HAS BEEN CREATED')

class BaseModel(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def insert(self): raise NotImplementedError
    
    @abstractmethod
    def update(self): raise NotImplementedError

    @abstractmethod
    def delete(self): raise NotImplementedError
    
    @abstractmethod
    def select(self): raise NotImplementedError

    @abstractmethod
    def select_all(self): raise NotImplementedError

class WebsiteModel(BaseModel):
    
    def __init__(self, con):
        self.db_con = con
    
    def insert(self, identifier, name_of_site, 
                     default_index, path_dir, 
                     prv, pub, version):

        self.db_con.execute('''
                   INSERT INTO website 
                   (identifier, name, default_index, path, size, prv, pub, version)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?);''', ( identifier, name_of_site, default_index, 
                                                          path_dir, os.stat(path_dir).st_size,
                                                          prv, pub, version ))
        self.db_con.commit()
    
    def update_upload(self, identifier): 
        sql = ''' UPDATE website SET is_uploaded = 1 WHERE identifier = ? ; '''                    
        cursor = self.db_con.cursor()
        cursor.execute(sql, (identifier,) )
        self.db_con.commit()
    
    def update(self, path_dir, 
           prv, 
           pub, 
           version, 
           default_index, 
           name_of_site):

        updated_at = datetime.today().strftime('%Y-%m-%d')
        self.db_con.execute('''
                                UPDATE website 
                                SET path = ?
                                , prv = ?
                                , pub = ?
                                , version = ?
                                , default_index = ?
                                , size = ?
                                , updated_at = ?
                                WHERE
                                name = ?;''', ( path_dir, 
                                                prv, 
                                                pub, 
                                                version, 
                                                default_index, 
                                                os.stat(path_dir).st_size,
                                                updated_at, 
                                                name_of_site ),)

        self.db_con.commit()
    
    def select_all(self, page): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM website LIMIT 10 OFFSET ?; ''', ((page - 1) * 10,))
        cursor_r = cursor.fetchone()
        return cursor_r
    
    def delete(self, name_of_site): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' DELETE website WHERE name = ?; ''', (name_of_site,))
        cursor_r = cursor.fetchone()
        self.db_con.commit()
        LOGGER.info('{0} HAS BEEN DELETED'.format(name_of_site))
        return cursor_r
    
    def check_if_website_exist(self, name_of_site):
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM website WHERE name = ?; ''', (name_of_site,))
        cursor_r = cursor.fetchone()
        self.db_con.commit()
        return cursor_r
    
    def check_if_website_uploaded(self, name_of_site):
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM website WHERE name = ? AND is_uploaded = 1; ''', (name_of_site,))
        cursor_r = cursor.fetchone()
        self.db_con.commit()
        return cursor_r

class ManifestModel(BaseModel):
    
    def __init__(self, con):
        self.db_con = con

    def insert(self, name,
                     metadata_content_type, 
                     size,
                     prv,
                     pub,
                     identifier):
        self.db_con.execute('''
                        INSERT INTO file_manifest (name, metadata_content_type, 
                        size, prv, pub, website_id)
                        VALUES (?, ?, ?, ?, ?, ?);''', ( name,
                                                         metadata_content_type, 
                                                         size,
                                                         prv,
                                                         pub,
                                                         identifier, ))
        self.db_con.commit()

    def update_upload(self, prv):
        sql = ''' UPDATE file_manifest SET is_uploaded = 1 WHERE prv = ? ; '''                    
        cur = self.db_con.cursor()
        cur.execute(sql, (prv,) )
        self.db_con.commit()

    def check_if_manifest_exist(self, prv, identifier):
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM file_manifest
                           WHERE prv = ? 
                           AND website_id = ? ; ''', (prv, identifier,))

        cursor_r = cursor.fetchone()
        self.db_con.commit()
        return cursor_r

    def select_belong_to_website(self, website_id): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM file_manifest
                           AND website_id = ? ; ''', (identifier,))

        cursor_r = cursor.fetchone()
        self.db_con.commit()
        return cursor_r

    def delete(self, id): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' DELETE file_manifest WHERE id = ?; ''', (id,))
        cursor_r = cursor.fetchone()
        self.db_con.commit()
        LOGGER.info('FILE HAS BEEN DELETED')
        return cursor_r

class SeparateModel(BaseModel):

    def __init__(self, con):
        self.db_con = con

    def insert(self, name, 
                     metadata_content_type, 
                     size,
                     uri,
                     identifier): 

        self.db_con.execute('''
            INSERT INTO file_separate ( name, metadata_content_type, 
            size, chk, website_id )
            VALUES (?, ?, ?, ?, ?);''', ( name, 
                                          metadata_content_type, 
                                          size,
                                          uri,
                                          identifier, ))
        self.db_con.commit()

    def update_upload(self, chk):
        sql = ''' UPDATE file_separate SET is_uploaded = 1 WHERE chk = ? ; '''
        cur = self.db_con.cursor()
        self.db_con.execute(sql, (chk,))
        self.db_con.commit()

    def check_if_chk_exist(self, chk, identifier):
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM file_separate 
                           WHERE chk = ? 
                           AND website_id = ? ; ''', (chk, identifier,))

        cursor_r = cursor.fetchone()
        self.db_con.commit()
        return cursor_r

    def select_belong_to_website(self, website_id): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' SELECT * FROM file_separate
                           AND website_id = ? ; ''', (identifier,))

        cursor_r = cursor.fetchone()
        self.db_con.commit()
        return cursor_r

    def delete(self, id): 
        cursor  = self.db_con.cursor()
        cursor.execute(''' DELETE file_separate WHERE name = ?; ''', (id,))
        cursor_r = cursor.fetchone()
        self.db_con.commit()
        LOGGER.info('FILE HAS BEEN DELETED')
        return cursor_r
