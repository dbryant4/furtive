#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" Manages the hashing of files """

import os
import hashlib
import logging
import multiprocessing


def hash_task(file_path, hash_algorithm='md5'):
    """ Responsible for hashing a file.

        This function reads in the file ``file_path`` in small chuncks the size
        of the hash algorithm's block size in order to avoid running out of
        memory. This means that this function should be able to read any file
        irregardless of the size.

        :param file_path: path of file to hash
        :type file_path: str

        :param hash_algorithm: the hashing algorithm to use. All options
                               available in `hashlib.algorithms` should work.
                               See:
                               https://docs.python.org/2/library/hashlib.html
        :type hash_algorithm: str

        :return: hash of file
        :return type: dict
    """

    with open(file_path, 'r') as file_to_hash:
        logging.debug('Starting Hash of %s', file_path)
        hash_object = hashlib.new(hash_algorithm)
        while True:
            chunk = file_to_hash.read(hash_object.block_size)
            if not chunk:
                break
            hash_object.update(chunk)
        file_hash = hash_object.hexdigest()
        logging.debug('Hash for %s: %s', file_path, file_hash)
    return {file_path: file_hash}


class HashDirectory(object):
    """ Object to manage hashing files in a directory.

        This object is responsible for walking the directory tree and
        adding each file to a list. Once the directory walk has compelted, each
        file path is passed to hash_task(). After each file has been
        hashed, this object will then create a Python dictionary of files with
        their associated hash.

        :param directory: Path to directory containing files
        :type directory: str

        :return: Dictionary of file:hash
        :return type: dict
    """

    def __init__(self, directory):
        self.directory = directory
        self.hashes = {}

    def hash_files(self):
        """ Orchestrates the discovery and hashing of files.



            Note: This method only supports the md5 hashing algorithm
        """

        files_to_hash = []
        num_processes = multiprocessing.cpu_count()

        logging.info('Discovering files in %s and adding to processing queue',
                     self.directory)
        for root, _, files in os.walk(self.directory):
            for found_file in files:
                full_path = os.path.join(root, found_file)
                relative_path = os.path.relpath(full_path, self.directory)
                logging.debug('Found %s', relative_path)
                files_to_hash.append(relative_path)

        logging.debug('Switching current working directory to %s',
                      self.directory)
        old_cwd = os.getcwd()
        os.chdir(self.directory)
        logging.debug('Starting %s hash worker processes', num_processes)
        pool = multiprocessing.Pool(processes=num_processes)
        logging.info('Hashing %s files', len(files_to_hash))
        results = pool.map(hash_task, files_to_hash)
        os.chdir(old_cwd)

        self.hashes = {}
        for item in results:
            self.hashes[item.keys()[0]] = item.values()[0]

        logging.debug('Ensuring processes have stopped')
        pool.close()
        pool.join()

        return self.hashes
