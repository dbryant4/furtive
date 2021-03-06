#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Furtive - File Integrity Verification System """

import os
import logging

from furtive.hasher import HashDirectory
from furtive.manifest import Manifest

__version__ = '0.4.0'


class Furtive(object):
    """ Furtive is an application which stores file state and allows users to
        verify the state in the future. Example use cases include file archives
        and file transport.

        If the manifest file exists, it will be automatcally loaded. Calling
        create() will overwrite the existing manifest in memory as well as the
        file.

        :param base_dir: Base directory to use for the manifest. Can be a full
                         or relative path.
        :type base_dir: str
        :param manifest_path: Path to the manifest file. Can be a full or
                              relative path.
        :type manifest_path: str
        :param exclude: list containing patterns to use to exclude files from
                        the manifest.
        :type exclude: list
    """

    def __init__(self, base_dir, manifest_path, exclude=None):
        self.base_dir = base_dir
        self.manifest_path = manifest_path
        self.exclude = [] if exclude is None else exclude
        self.manifest = Manifest(self.base_dir,
                                 self.manifest_path,
                                 self.exclude)

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
            raise RuntimeError('Manifest {0!s} not loaded.'
                               .format(self.manifest_path))

        logging.info('Generating temporary updated manifest.')
        current_manifest = Manifest(self.base_dir, '/dev/null')
        current_manifest.create()

        logging.info('Generating list of changed files')

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
