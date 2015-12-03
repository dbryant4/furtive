""" Test cases for HashTask object """

import os
import sys
import imp
import unittest

from StringIO import StringIO

from mock import MagicMock, patch

furtive = imp.load_source('furtive', 'scripts/furtive')

class TestScriptFurtive(unittest.TestCase):
    """ Test cases for furtive script which is the cli "binary" """

    def setUp(self):
        if os.path.exists('.test_manifest.db'):
            os.unlink('.test_manifest.db')
        if os.path.exists('test-data/test-file'):
            os.unlink('test-data/test-file')

    def test_parse_args(self):
        """ Ensure parsing of proper arguments """

        args = '--basedir test-data --manifest .test_manifest.db create'
        parsed_args = furtive.parse_args(args.split())

        self.assertEqual(parsed_args.basedir, 'test-data')
        self.assertEqual(parsed_args.manifest_path, '.test_manifest.db')
        self.assertEqual(parsed_args.action, 'create')
        self.assertEqual(parsed_args.log_level, 'info')


    def test_create(self):
        """ Ensure a manifest can be created using the furtive script """

        args = 'app.py --basedir test-data --manifest .test_manifest.db create'
        sys.argv = args.split()

        furtive.main()

        self.assertTrue(os.path.exists('.test_manifest.db'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_compare(self, mock_stdout):
        """ Ensure a manifest can be compared to current files """

        args = 'app.py --basedir test-data --manifest .test_manifest.db create'
        sys.argv = args.split()

        furtive.main()

        with open('test-data/test-file', 'w') as text_file:
            text_file.write('This is a test file.')

        args = 'app.py --basedir test-data --manifest .test_manifest.db compare'
        sys.argv = args.split()
        furtive.main()

        self.assertTrue('test-data/test-file' in mock_stdout.getvalue())

    def tearDown(self):
        if os.path.exists('.test_manifest.db'):
            os.unlink('.test_manifest.db')
        if os.path.exists('test-data/test-file'):
            os.unlink('test-data/test-file')

if __name__ == '__main__':
    unittest.main()
