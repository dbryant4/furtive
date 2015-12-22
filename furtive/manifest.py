#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Manifest of files and their hashes """

import logging

from yaml import load, dump
try:
    from yaml import CSafeLoader as Loader, CSafeDumper as Dumper
except ImportError:
    from yaml import SafeLoader as Loader, SafeDumper as Dumper

from furtive.hasher import HashDirectory


class Manifest(object):
    """ Manifest of files and the associated hashes.

        :param directory: directory which will serve as the root for the
                          manifest. All files under the directory will be
                          hashed and added to or compared with the manifest.
        :param type: str
        :param manifest_file: file location of the manifest file. This is the
                              path which will be used for the ``create()`` and
                              ``compare()`` methods. If the file exists, the
                              ``create()`` method will overwrite it.
        :param exclude: list containing patterns to use to exclude files from
                        the manifest.
        :type exclude: list
    """

    def __init__(self, directory, manifest_file, exclude=None):
        self.directory = directory
        self.manifest_file = manifest_file
        self.manifest = None
        self.exclude = [] if exclude is None else exclude

    def __getitem__(self, hashed_file):
        return self.manifest[hashed_file]

    def create(self):
        """ Creates a new manifest from the directory by calling
            furtive.hasher.HashDirectory() and placing the return dictionary
            in to `Manifest.manifest`.
        """

        self.manifest = HashDirectory(self.directory,
                                      self.exclude).hash_files()

    def load(self):
        """ Load a manifest from the manifest file.

            This method will open the manfiest YAML file and load it in to
            the `manifest` object variable.
        """

        logging.debug('Opening %s', self.manifest_file)
        with open(self.manifest_file, 'r') as manifest_file:
            self.manifest = load(manifest_file.read(), Loader=Loader)

    def save(self):
        """ Save the manifest to the manifest file.

            Open a YAML file and dump the contents of the manifest to it.
        """

        logging.info('Saving manifest to %s', self.manifest_file)
        logging.debug('Opening %s', self.manifest_file)
        with open(self.manifest_file, 'w') as manifest_file:
            manifest_file.write(dump(self.manifest,
                                     default_flow_style=False,
                                     Dumper=Dumper))

        logging.debug('Manifest saved')

    def is_empty(self):
        """ Determines if the manifest within memory is empty.

            This simply checks to see if the manifest is None.

            :return: True if manifest is empty, False otherwise.
            :return type: bool
        """

        return self.manifest is None
