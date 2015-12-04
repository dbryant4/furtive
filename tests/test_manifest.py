""" Test cases for HashTask object """

import os
import unittest

from furtive.manifest import Manifest

class TestManifest(unittest.TestCase):

    def test_manifest_create(self):
        """ Ensure a manifest can be generated from a directory """

        manifest = Manifest('test-data', '.test_manifest.yaml')
        manifest.create()

        self.assertEqual(manifest['test-data/documents/Important Document 1.odt'], 'd460a36805fb460c038d96723f206b20')
        self.assertEqual(manifest['test-data/documents/Important Presentation.odp'], '1911ec839cedcbf00739a7d3447ec3a3')
        self.assertEqual(manifest['test-data/pictures/Picture #1.jpg'], '6eec850e32622c0e33bdae08ced29e24')
        self.assertEqual(manifest['test-data/documents/exclude_me.txt'], '2e7d8cb32bb82e838506aff5600182d1')
        self.assertEqual(len(manifest.manifest), 4)

    def test_manifest_save(self):
        """ Ensure the manifest can be successfully saved to a sqllite db """

        manifest = Manifest('test-data', '.test_manifest.yaml')
        manifest.create()
        manifest.save()

        self.assertTrue(os.path.isfile('.test_manifest.yaml'))
        with open('.test_manifest.yaml', 'r') as manifest_file:
            self.assertTrue('test-data/pictures/Picture #1.jpg' in manifest_file.read())

    def test_manifest_load(self):
        """ Ensure the manifest can be loaded from a sqlite3 database """

        self.test_manifest_save()

        manifest = Manifest('test-data', '.test_manifest.yaml')
        self.assertTrue(manifest.manifest is None)
        manifest.load()

        self.assertEqual(manifest['test-data/documents/Important Document 1.odt'], 'd460a36805fb460c038d96723f206b20')
        self.assertEqual(manifest['test-data/documents/Important Presentation.odp'], '1911ec839cedcbf00739a7d3447ec3a3')
        self.assertEqual(manifest['test-data/pictures/Picture #1.jpg'], '6eec850e32622c0e33bdae08ced29e24')
        self.assertEqual(manifest['test-data/documents/exclude_me.txt'], '2e7d8cb32bb82e838506aff5600182d1')
        self.assertEqual(len(manifest.manifest), 4)

    def tearDown(self):
        if os.path.exists('.test_manifest.yaml'):
            os.unlink('.test_manifest.yaml')

if __name__ == '__main__':
    unittest.main()
