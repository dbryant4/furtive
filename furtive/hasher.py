#! /usr/bin/env python
# -*- coding: utf-8 -*-

""" Manages the hashing of files """

import os
import time
import hashlib
import logging
import multiprocessing


class HashProcess(multiprocessing.Process):
    """ multiprocessing process object which will process HashTask() objects """

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                self.task_queue.task_done()
                break
            logging.debug('Hashing %s' % next_task.file_path)
            answer = next_task()
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return

class HashTask(object):
    """ A file hash task

        This task is responsible for hashing a file. It returns itself once
        hasing is complete thereby allowing the object to be placed in a queue
        and returned to the main thread.

        :param file_path: Path to a file
        :param type: str

        :return: The object which contains `file_path` and `hash` variables.
        :return type: HashTask
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.hash = None

    def __call__(self):
        with open(self.file_path, 'r') as file_to_hash:
            self.hash = hashlib.md5(file_to_hash.read()).hexdigest()
            logging.debug('Hash for %s: %s' % (self.file_path, self.hash))

        return self

    def __str__(self):
        return self.hash


class HashDirectory(object):
    """ Object to manage hashing files in a directory.

        This object is responsible for walking the directory tree and
        creating HashTask() objects for each file. After each file has been
        hashed, this object will then create a Python dictionary of files with
        their associated hash.

        :param directory: Path to directory containing files
        :type directory: str

        :return: Dictionary of file:hash
        :return type: dict
    """

    def __init__(self, directory):
        self.directory = directory

    def hash_files(self):
        """ Orchestrates the discovery and hashing of files.

            This method sets up queues to be used by the HashProcess() object.
            Next, file discovery begins. As a file is found, an instance of
            HashTask() is created and pushed to the tasks queue.

            Then, it starts N number of worker processes (HashProcess()) to
            process HashTasks(). N is equal to the number of CPUs.

            Once all of the files have been discovered, "None" tasks are placed
            on to the tasks queue to indicate to the workers that they should
            stop execution.

            After all workers have stopped, the results are processed and a
            dictionary is created where the key is the file path and the key is
            the hash value. This dicitonary is returned.

            Note: This method only supports the md5 hashing algorithm
        """

        tasks = multiprocessing.JoinableQueue()
        results = multiprocessing.Queue()
        num_processes = multiprocessing.cpu_count()


        logging.info('Discovering files in %s and adding to processing queue' %\
            self.directory)
        for root, dirs, files in os.walk(self.directory):
            map((lambda x: tasks.put(HashTask(os.path.join(root, x)))), files)


        for i in xrange(num_processes):
            tasks.put(None)

        logging.debug('Starting %s HashProcess workers' % num_processes)
        hashers = [HashProcess(tasks, results) for i in xrange(num_processes)]
        for hasher in hashers:
            hasher.start()

        tasks.join()

        hashes = {}
        while not results.empty():
            result = results.get()
            hashes[result.file_path] = result.hash

        return hashes
