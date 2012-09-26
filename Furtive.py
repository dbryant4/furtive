#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
"""
Furtive. Deal with it!
"""

import os
import hashlib
import sys
import sqlite3

class Furtive:
    """
       Furtive: file integrity verification system. 
    """
    conn = None
    cur = None
    _file_list_intersect = None
    verbose = False
    dir = ""
    file_list = None
    prev_file_list = None
    hashes = None
    prev_hashes = None
    added = None
    removed = None
    unchanged = None
    changed = None
    hashList = {}
    manifestFile = ".manifest.db"
    
    def __init__(self, dir, verbose=False):
        self.dir = dir
        self.verbose = verbose
    
    def __openDB(self):        
        """Open sqlite database"""
        try:
            self.conn = sqlite3.connect(os.path.join(self.dir, self.manifestFile))
            self.cur = self.conn.cursor()
            self.cur.execute("CREATE TABLE IF NOT EXISTS filehashes(filename TEXT, hash TEXT)")
        except sqlite3.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)
    
    def __closeDB(self):
        """Close sqlite database"""
        self.conn.commit()
        self.cur = None
    
    def __truncateDB(self):
        """Truncate (delete) manifest file"""
        self.cur.execute("DELETE FROM filehashes")
    
    def set_verbosity(self, verbosity):
        """Turn on verbose output. Values: True or False"""
        self.verbosity = verbosity
    
    def set_directory(self, dir):
        """Set the root directory where to be manifested files are located"""
        self.dir = dir
    
    def set_manifest(self, manifest_file):
        """Set manifest file to manifest_file"""
        self.manifestFile = manifest_file
     
    def get_files(self,dir = None):
        """Generate a set consisting of files relative to the given dir."""
        if dir is None:
            dir = self.dir
        
        fileSet = set()
        for root, dirs, files in os.walk(dir):
            for file in files:
                # Full file path (ex. /etc/rc.d/rc.1/test)
                full_path = os.path.join(root, file)
                # Reative to dir (ex rc.d/rc.1/test)
                relative_path = os.path.relpath(full_path, dir)
                if self.verbose == True:
                    sys.stderr.write("Found File: " + relative_path + "\n")
                fileSet.add(relative_path)
        return fileSet
    
    def hash_files(self,fileSet):
        """Hash each file in the set fileSet. Returns a dict of reltive_path/file: hash"""
        hashList = {}
        for file in fileSet:
            if self.verbose == True:
                sys.stderr.write("Hashing: " + os.path.join(self.dir, file) + "\n")
 
            # Full file path (ex. /etc/rc.d/rc.1/test)
	    full_path = os.path.join(self.dir, file)

	    # Open file, read it, hash it, place hash in 
            with open(full_path,'r') as f:
                m = hashlib.sha1()
                while True:
                    chunk = f.read(m.block_size)
                    if not chunk:
                       break
                    m.update(chunk)
            hash = m.hexdigest()
	    if self.verbose == True:
	        sys.stderr.write(hash + " " + file + "\n")
	    #Put hash in dictionary
	    hashList[file]=hash
            f.close()
        return hashList
     
    def get_previous_hashes(self,dir = None):
        """
           Get hash dictionary from sqlite3 DB
        """
        if not os.path.isfile(self.manifestFile):
            return {}

        self.__openDB()
            
        # If no dir is provided when calling this method, use object's dir
        if dir is None:
            dir = self.dir
       
        # Run SQL to pull stuff from the DB 
        try:
            self.cur.execute("SELECT * FROM filehashes");
        except sqlite3.Error, e:
            sys.stderr.write("Error " + e.args[0] + ":\n")
            sys.exit(1)
        else:
            fetchedHashes = self.cur.fetchall()
            # Fetch rows and place in a dict we can use
            hashes = {}
            for file, hash in fetchedHashes:
                hashes[file] = hash
            return hashes
        self.__closeDB()
    
    def update_manifest(self, hashedFileList = None):
        """
           Save hashes to manifest file. Currently simply truncates the 
           manifest and writes everything to the DB
        """

        if hashedFileList is None:
            hashedFileList = self.hashes

        self.__openDB()
        self.__truncateDB()
        if hashedFileList is None:
            hashedFileList = self.hashList

        # Try to insert hashes in DB
        try:
            for file, hash in hashedFileList.iteritems():
                self.cur.execute('INSERT INTO filehashes VALUES (?,?)',(file, hash));
                if self.verbose == True:
                    sys.stderr.write("Inserted Hash in DB for: " + file + "\n")
        except sqlite3.Error, e:
            sys.stderr.write("Error " + e.args[0] + ":\n")
            sys.exit(1)
        self.__closeDB()

    def compare(self):
        """ Tell Furtive to hash the files in the provided dir and 
            then compare them with the previous hashes 
        """ 
        # Get set of files on file system
        self.file_list = self.get_files()
        
        # Hash files and place within object
        self.hashes = self.hash_files(self.file_list)

        # Get old hashes from manifest
        self.prev_hashes = self.get_previous_hashes()
        self.prev_file_list = set(self.prev_hashes.keys())
        
        # Find Intersection
        self._file_list_intersect = self.prev_file_list.intersection(self.file_list)

        # Find files added
        self.added = self.file_list - self.prev_file_list

        # Next, see what files been removed
        self.removed = self.prev_file_list - self.file_list

        # Check to see what has changed
        self.changed = set()
        self.unchanged = set()
        for o in self._file_list_intersect:
            if self.prev_hashes[o] != self.hashes[o]:
                self.changed.add(o)
            else:
                self.unchanged.add(o)

    def get_hash(self,file):
        """
           Returns the computed hash of the file using the current contents.
        """
        if self.hashes is None:
            return None
        return self.hashes[file]

    def get_previous_hash(self,file):
        """
           Returns the hash stored in the manifest.
        """
        if self.prev_hashes is None:
            return None
        return self.prev_hashes[file]
