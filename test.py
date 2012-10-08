#! /usr/bin/env python 
# -*- coding: utf-8 -*- 

import os
import sys
import unittest
from Furtive import Furtive

class FurryTest(unittest.TestCase):

    def setUp(self):
        self.fur = Furtive(os.path.join(sys.path[0], "test-data"))
        self.expected_hashes = {'documents/Important Document 1.odt':
                                    'f3da38b41448e9ca807cf4a0f6f9e793aeaeea11', 
                                'pictures/Picture #1.jpg': 
                                    '86ce5b81a8586c297b52c31baa00985716f462b6', 
                                'documents/Important Presentation.odp': 
                                    'cfddfd85367a9fa9ea1207a97db0e377ffbcbf9d'
                               } 

    def test_compare(self):
        self.fur.compare()

        # Compare number of files in each hash list
        self.assertTrue(len(self.expected_hashes) == len(self.fur.hashes))

        # Test compare dicts with hashes
        for file, hash in self.expected_hashes.iteritems():
            self.assertTrue(hash == self.fur.hashes[file])

        # Number of added files should equal number of expected files
        self.assertTrue(len(self.fur.added) == len(self.expected_hashes))
        # Should be 0 removed, unchanged, or changed files
        self.assertTrue(len(self.fur.changed) == 0)
        self.assertTrue(len(self.fur.removed) == 0)
        self.assertTrue(len(self.fur.unchanged) == 0)

    def test_manifest_update(self):
        self.fur.compare()
        self.fur.update_manifest()

        # Make sure manifest is written and exists
        self.assertTrue(os.path.isfile(os.path.join(sys.path[0], "test-data", self.fur.manifest_file)))

    def test_previous_manifest(self):
        self.fur.compare()
        self.fur.update_manifest()

        # Compare hashes again
        self.fur.compare() 

        # Number of unchanged files should equal expected_hashes
        self.assertTrue(len(self.expected_hashes) == len(self.fur.unchanged))

        # should be 0 removed, added, or changed files
        self.assertTrue(len(self.fur.changed) == 0)
        self.assertTrue(len(self.fur.removed) == 0)
        self.assertTrue(len(self.fur.added) == 0)

        # Test compare dicts with hashes
        for file, hash in self.expected_hashes.iteritems():
            self.assertTrue(hash == self.fur.hashes[file])

    def tearDown(self):
        os.remove(os.path.join(sys.path[0], "test-data", self.fur.manifest_file))
        # Make sure manifest is deleted
        self.assertFalse(os.path.isfile(os.path.join(sys.path[0], "test-data", self.fur.manifest_file)))

if __name__ == '__main__':
    unittest.main()