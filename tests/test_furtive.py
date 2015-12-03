""" Test cases for HashTask object """

import os
import unittest

from furtive import Furtive

class TestFurtive(unittest.TestCase):

    def setUp(self):
        self.furtive = Furtive('test-data', '.test_manifest.db')
        self.furtive.create()

    def test_furtive_create(self):
        """ Ensure a manifest can be created """

        self.assertEqual(self.furtive.manifest.manifest['test-data/documents/Important Document 1.odt'], 'd460a36805fb460c038d96723f206b20')
        self.assertEqual(self.furtive.manifest.manifest['test-data/documents/Important Presentation.odp'], '1911ec839cedcbf00739a7d3447ec3a3')
        self.assertEqual(self.furtive.manifest.manifest['test-data/pictures/Picture #1.jpg'], '6eec850e32622c0e33bdae08ced29e24')
        self.assertEqual(self.furtive.manifest.manifest['test-data/documents/exclude_me.txt'], '2e7d8cb32bb82e838506aff5600182d1')
        self.assertEqual(len(self.furtive.manifest.manifest), 4)

    def test_compare_added(self):
        """ Ensure comparison reports added files correctly """

        with open('test-data/test-file', 'w') as text_file:
            text_file.write('This is a test file.')

        furtive = Furtive('test-data', '.test_manifest.db')
        changes = furtive.compare()

        self.assertEqual(changes['added'], ['test-data/test-file'])
        self.assertEqual(changes['removed'], [])
        self.assertEqual(changes['changed'], [])

    def test_compare_removed(self):
        """ Ensure comparison reports removed files correctly """

        with open('test-data/test-file', 'w') as text_file:
            text_file.write('This is a test file.')

        self.furtive.create()

        os.unlink('test-data/test-file')
        changes = self.furtive.compare()

        self.assertEqual(changes['added'], [])
        self.assertEqual(changes['removed'], ['test-data/test-file'])
        self.assertEqual(changes['changed'], [])

    def test_compare_changed(self):
        """ Ensure comparison reports changed files correctly """

        with open('test-data/test-file', 'w') as text_file:
            text_file.write('This is a test file.')

        self.furtive.create()

        with open('test-data/test-file', 'w') as text_file:
            text_file.write('This file has been changed')

        changes = self.furtive.compare()

        self.assertEqual(changes['added'], [])
        self.assertEqual(changes['removed'], [])
        self.assertEqual(changes['changed'], ['test-data/test-file'])
        
    def tearDown(self):
        if os.path.exists('.test_manifest.db'):
            os.unlink('.test_manifest.db')
        if os.path.exists('test-data/test-file'):
            os.unlink('test-data/test-file')

if __name__ == '__main__':
    unittest.main()
