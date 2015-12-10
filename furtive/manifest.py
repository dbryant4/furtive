#! /usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import sqlite3
import logging

from furtive.hasher import HashDirectory


class Manifest(object):

    def __init__(self, directory, manifest_file):
        self.directory = directory
        self.manifest_file = manifest_file
        self.manifest = None

    def __getitem__(self, file):
        return self.manifest[file]

    def create(self):
        """ Creates a new manifest from the directory by calling
            furtive.hasher.HashDirectory() and placing the return dictionary
            in to `Manifest.manifest`.
        """

        self.manifest = HashDirectory(self.directory).hash_files()

    def load(self):
        """ Load a manifest from the manifest file.

            This method will open the manfiest YAML file and load it in to
            the `manifest` object variable.
        """

        logging.debug('Opening %s' % self.manifest_file)
        with open(self.manifest_file, 'r') as manifest_file:
            self.manifest = yaml.load(manifest_file.read())

    def save(self):
        """ Save the manifest to the manifest file.

            Open a YAML file and dump the contents of the manifest to it.
        """

        logging.info('Saving manifest to %s' % self.manifest_file)
        logging.debug('Opening %s' % self.manifest_file)
        with open(self.manifest_file, 'w') as manifest_file:
            manifest_file.write(yaml.safe_dump(self.manifest,
                                default_flow_style=False))

        logging.debug('Manifest saved')

    def is_empty(self):
        """ Determines if the manifest within memory is empty.

            This simply checks to see if the manifest is None.

            :return: True if manifest is empty, False otherwise.
            :return type: bool
        """

        return self.manifest is None
