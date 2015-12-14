#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Furtive - File Integrity Verification System """


import os
import logging

from .hasher import HashDirectory
from .manifest import Manifest


class Furtive(object):
    """ Furtive is an application which stores file state and allows users to
        verify the state in the future. Example use cases include file archives
        and file transport.

        :param base_dir: Base directory to use for the manifest. Can be a full
                         or relative path.
        :type base_dir: str
        :param manifest_path: Path to the manifest file. Can be a full or
                              relative path.
        :type manifest_path: str

    """

    def __init__(self, base_dir, manifest_path):
        self.base_dir = base_dir
        self.manifest_path = manifest_path
        self.manifest = Manifest(self.base_dir, self.manifest_path)

        if os.path.exists(manifest_path):
            self.manifest.load()

    def create(self):
        """ Create and save a new manifest.

            The contents of the new Manfiest() will be saved to
            `manifest_path`.

            :return: None
        """

        self.manifest.create()
        self.manifest.save()

    def compare(self):
        """ Compare the hashes in the database with the current hashes of files
            on the file system.

            :return: Dictionary of added, deleted, and changed files.
            :return type: dict
        """

        if self.manifest.is_empty():
            raise RuntimeError('Manifest %s not loaded.' % self.manifest_path)

        logging.info('Generating temporary updated manifest.')
        current_manifest = Manifest(self.base_dir, '/dev/null')
        current_manifest.create()

        added_files = list(set(current_manifest.manifest) -
                           set(self.manifest.manifest))
        removed_files = list(set(self.manifest.manifest) -
                             set(current_manifest.manifest))
        common_files = list(set(self.manifest.manifest) &
                            set(current_manifest.manifest))
        changed_files = [common_file for common_file in common_files
                         if current_manifest[common_file] !=
                         self.manifest[common_file]]

        return {'removed': removed_files,
                'added': added_files,
                'changed': changed_files}
