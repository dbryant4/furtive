#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import logging

from furtive.hasher import HashTask, HashProcess, HashDirectory

class Manifest(object):

    def __init__(self, directory, manifest_file):
        self.directory = directory
        self.manifest_file = manifest_file
        self.manifest = None

    def create(self):
        """ Creates a new manifest from the directory by calling
            furtive.hasher.HashDirectory() and placing the return dictionary
            in to `Manifest.manifest`.
        """

        self.manifest = HashDirectory(self.directory).hash_files()

    def load(self):
        """ Load a manifest from the sqlite database.

            This method will open the manfiest sqlite database and read
            all of the hashes and load them in the the manifest object variable.
        """

        logging.debug('Opening %s' % self.manifest_file)
        with sqlite3.connect(self.manifest_file) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM filehashes");
            manifest = cursor.fetchall()

        self.manifest = {}
        for x in manifest:
            self.manifest[x[0]] = x[1]

    def save(self):
        """ Save the manifest to the database.

            Open a sqlite3 database, truncate it, then write the manifest to it.
        """

        logging.debug('Opening %s' % self.manifest_file)
        with sqlite3.connect(self.manifest_file) as connection:
            cursor = connection.cursor()
            connection.text_factory = str
            cursor.execute("CREATE TABLE IF NOT EXISTS filehashes(filename TEXT, hash TEXT)")
            cursor.execute("DELETE FROM filehashes")
            for file_name, md5_hash in self.manifest.iteritems():
                logging.debug('Saving hash for %s' % file_name)
                cursor.execute('INSERT INTO filehashes VALUES (?,?)',(file_name.decode('utf-8'), md5_hash));
            connection.commit()
            cursor = None
        logging.debug('Manifest saved')


    def is_empty(self):
        """ Determines if the manifest within memory is empty.

            This simply checks to see if the manifest is None.

            :return: True if manifest is empty, False otherwise.
            :return type: bool
        """

        return self.manifest is None
