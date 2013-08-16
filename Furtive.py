#! /usr/bin/env python 
# -*- coding: utf-8 -*- 
"""
Furtive. Deal with it!
"""

import os
import hashlib
import sys
import sqlite3
import fnmatch
import logging

class Furtive:
    """
       Furtive: file integrity verification system. 
    """

    
    def __init__(self, dir, verbose=False):
        self.dir = dir
        self.verbose = verbose
        self.conn = None
        self.cur = None
        self._file_list_intersect = None
        self.show_progress_indicator = False
        self.file_list = None
        self.prev_file_list = None
        self.hashes = None
        self.prev_hashes = None
        self.added = None
        self.removed = None
        self.unchanged = None
        self.changed = None
        self.hashList = {}
        self.manifest_file = ".manifest.db"
        self.hash_algorithm = "sha1"

    def __openDB(self):        
        """
        Open sqlite database
        """
        
        old_cwd = os.getcwd()
        try:
            os.chdir(self.dir)
            self.conn = sqlite3.connect(self.manifest_file)
            os.chdir(old_cwd)
            self.cur = self.conn.cursor()
            self.conn.text_factory = str
            self.cur.execute("CREATE TABLE IF NOT EXISTS filehashes(filename TEXT, hash TEXT)")
        except:
            raise

    def __closeDB(self):
        """
        Close sqlite database
        """

        self.conn.commit()
        self.cur = None
    
    def __truncateDB(self):
        """
        Truncate (delete) manifest file
        """

        self.cur.execute("DELETE FROM filehashes")
    
    def set_verbosity(self, verbosity):
        """Turn on verbose output. Values: True or False"""
        self.verbosity = verbosity
    
    def set_directory(self, dir):
        """
        Set the root directory where to be manifested files are located
        """

        self.dir = dir
    
    def set_manifest(self, manifest_file):
        """
        Set manifest file to manifest_file
        """

        self.manifest_file = manifest_file

    def set_hash_algorithm(self, algorithm):
        """
        Set the algorithm to use when hashing files. 
        algorithm may be any algorithm offered up by the local openssl 
        installation.
        """
        
        try:
            hashlib.new(algorithm)
        except: 
            raise
        else:
            self.hash_algorithm = algorithm
    
     
    def show_progress(self, progress=False):
        """ 
        Show a progress indicator on STDOUT.
        Default: False
        """

        self.show_progress_indicator = progress

    def get_files(self, dir=None, excludes=[]):
        """
        Generate a set consisting of files relative to the given dir.
            dir: Directory to use as the root of the manifest
            excludes: Optional dictionary of file patterns to exclude. 
                      These patterns are matched to the absolute path.
        """

        if dir is None:
            dir = self.dir
        
        file_set = set()
        for root, dirs, files in os.walk(dir):
            for file in files:
                # Full file path (ex. /etc/rc.d/rc.1/test)
                full_path = os.path.join(root, file)
                # Reative to dir (ex rc.d/rc.1/test)
                relative_path = os.path.relpath(full_path, dir)
                # Skip manifest file
                if relative_path == self.manifest_file:
                    continue
                if self.verbose == True:
                    sys.stderr.write("Found File: " + relative_path + "\n")
                # Skip excludes. Can be improved...
                for exclude in excludes:
                    if fnmatch.fnmatch(full_path,exclude):
                        # Add log message saying skiped file due to exclusion
                        break
                else:
                    file_set.add(relative_path)
                    # Add message saying added file to file set
        return file_set
    
    def hash_files(self, file_set):
        """
        Hash each file in the set fileSet. Returns a dict of reltive_path/file: hash
        """

        hash_list = {}
        file_num = 0
        total_num_files = len(file_set)
        for file in file_set:
            file_num = file_num + 1
            if self.verbose == True:
                sys.stderr.write("Hashing: " + os.path.join(self.dir, file) + "\n")
            if self.show_progress_indicator:
                progress = round((float(file_num) / total_num_files) * 100,1)
                sys.stdout.write("\r" + str(progress) + "% " + 
                    str(file_num) + " of " + str(total_num_files))
                sys.stdout.flush()
            # Full file path (ex. /etc/rc.d/rc.1/test)
            full_path = os.path.join(self.dir, file)
            
            total_size = os.path.getsize(full_path)

            # Open file, read it, hash it, place hash in 
            with open(full_path,'r') as f:
                #m = hashlib.sha1()
                m = hashlib.new(self.hash_algorithm)
                loops = 0
                while True:
                    chunk = f.read(m.block_size)
                    if not chunk:
                       break
                    m.update(chunk)
                    loops = loops + 1
                    if self.show_progress_indicator:
                        file_progress = round((float(loops) * float(m.block_size)) / total_size * 100,1)
                        sys.stdout.write("\r" + str(progress) + "% " + 
                            str(file_num) + " of " + str(total_num_files) + 
                            " File: " + str(file_progress) + "%  ")
                        sys.stdout.flush()

            hash = m.hexdigest()
	    if self.verbose == True:
	        sys.stderr.write(hash + " " + file + "\n")
	    #Put hash in dictionary
	    hash_list[file] = hash
            f.close()
        return hash_list
     
    def get_previous_hashes(self, dir=None):
        """
           Get hash dictionary from sqlite3 DB
        """

        if not os.path.isfile(self.manifest_file):
            #os.path.join(self.dir, self.manifest_file)
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
            raise
        except:
            raise
        else:
            fetched_hashes = self.cur.fetchall()
            # Fetch rows and place in a dict we can use
            hashes = {}
            for file, hash in fetched_hashes:
                hashes[file] = hash
            return hashes
        self.__closeDB()
    
    def update_manifest(self, hashed_file_list=None):
        """
           Save hashes to manifest file. Currently simply truncates the 
           manifest and writes everything to the DB
        """

        if hashed_file_list is None:
            hashed_file_list = self.hashes

        self.__openDB()
        self.__truncateDB()

        # Try to insert hashes in DB
        try:
            for file, hash in hashed_file_list.iteritems():
                self.cur.execute('INSERT INTO filehashes VALUES (?,?)',(file.decode('utf-8'), hash));
                if self.verbose == True:
                    sys.stderr.write("Inserted Hash in DB for: " + file + "\n")
        except sqlite3.Error, e:
            sys.stderr.write("Error " + e.args[0] + ":\n")
            raise
        except:
            raise
        self.__closeDB()

    def compare(self, excludes=[]):
        """ Tell Furtive to hash the files in the provided dir and 
            then compare them with the previous hashes 
        """ 

        # Get set of files on file system
        self.file_list = self.get_files(self.dir,excludes)
        
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

    def get_hash(self, file):
        """
           Returns the computed hash of the file using the current contents.
        """

        if self.hashes is None:
            return None
        return self.hashes[file]

    def get_previous_hash(self, file):
        """
           Returns the hash stored in the manifest.
        """

        if self.prev_hashes is None:
            return None
        return self.prev_hashes[file]
