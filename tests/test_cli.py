""" Test cases for furtive script """

import os
import sys
import imp
import yaml
import unittest

from StringIO import StringIO

from mock import MagicMock, patch

from furtive import cli

class TestScriptFurtive(unittest.TestCase):
    """ Test cases for furtive script which is the cli "binary" """

    def setUp(self):
        """ Common setup tasks for all tests in this test case """

        if os.path.exists('.test_manifest.yaml'):
            os.unlink('.test_manifest.yaml')
        if os.path.exists('tests/fixtures/test-data/test-file'):
            os.unlink('tests/fixtures/test-data/test-file')
        if os.path.exists('tests/fixtures/report.yml'):
            os.unlink('tests/fixtures/report.yml')

    def test_parse_args(self):
        """ Ensure parsing of proper arguments """

        args = '--basedir tests/fixtures/test-data --manifest .test_manifest.yaml create'
        parsed_args = cli.parse_args(args.split())

        self.assertEqual(parsed_args.basedir, 'tests/fixtures/test-data')
        self.assertEqual(parsed_args.manifest_path, '.test_manifest.yaml')
        self.assertEqual(parsed_args.action, 'create')
        self.assertEqual(parsed_args.log_level, 'info')


    def test_create(self):
        """ Ensure a manifest can be created using the furtive cli """

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml create'
        sys.argv = args.split()

        cli.main()

        self.assertTrue(os.path.exists('.test_manifest.yaml'))

    @patch('sys.stdout', new_callable=StringIO)
    def test_compare(self, mock_stdout):
        """ Ensure a manifest can be compared to current files """

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml create'
        sys.argv = args.split()

        cli.main()

        with open('tests/fixtures/test-data/test-file', 'w') as text_file:
            text_file.write('This is a test file.')

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml compare'
        sys.argv = args.split()
        cli.main()

        self.assertTrue('test-file' in mock_stdout.getvalue())
        self.assertTrue('!!python/unicode' not in mock_stdout.getvalue())

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml create'
        sys.argv = args.split()
        cli.main()

        with open('tests/fixtures/test-data/test-file', 'w') as text_file:
            text_file.write('This is a test file with changed content.')

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml compare'
        sys.argv = args.split()
        cli.main()

        self.assertTrue('test-file' in mock_stdout.getvalue())
        self.assertTrue('!!python' not in mock_stdout.getvalue())


    @patch('sys.stdout', new_callable=StringIO)
    def test_quiet(self, mock_stdout):
        """ Ensure nothing is printed to stdout if --quiet is provided.

            Basically re-running test_compare() but with the --quiet arg.
        """

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml create --quiet'
        sys.argv = args.split()

        cli.main()

        with open('tests/fixtures/test-data/test-file', 'w') as text_file:
            text_file.write('This is a test file.')

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml compare --quiet'
        sys.argv = args.split()
        cli.main()

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml create --quiet'
        sys.argv = args.split()
        cli.main()

        with open('tests/fixtures/test-data/test-file', 'w') as text_file:
            text_file.write('This is a test file with changed content.')

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml compare --quiet'
        sys.argv = args.split()
        cli.main()

        stdout = mock_stdout.getvalue()
        self.assertTrue(stdout == '', msg=stdout)

    def test_check(self):
        """ Ensure exit with 1 if check action is provided. """

        # Create manifest
        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml create'
        sys.argv = args.split()
        cli.main()

        # Compare without making changes. Should not raise exception.
        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml check'
        sys.argv = args.split()
        cli.main()

        # Create a file and run check agian. Should exit with 1
        with open('tests/fixtures/test-data/test-file', 'w') as text_file:
            text_file.write('This is a test file.')

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml check'
        sys.argv = args.split()
        with self.assertRaises(SystemExit) as return_status:
            cli.main()
            self.assertEqual(return_status.exception.code, 1)

        # Add the new file to the manifest, then change it. Should exit with 1
        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml create'
        sys.argv = args.split()
        cli.main()

        with open('tests/fixtures/test-data/test-file', 'w') as text_file:
            text_file.write('This is a changed test file.')

        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml check'
        sys.argv = args.split()
        with self.assertRaises(SystemExit) as return_status:
            cli.main()
            self.assertEqual(return_status.exception.code, 1)

        # delete test file then run compare. Should exit with 1
        os.unlink('tests/fixtures/test-data/test-file')
        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml check'
        sys.argv = args.split()
        with self.assertRaises(SystemExit) as return_status:
            cli.main()
            self.assertEqual(return_status.exception.code, 1)

    def test_write_report_to_file(self):
        """ Ensure the diff report can be written to a file. """

        # Create manifest
        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml create'
        sys.argv = args.split()
        cli.main()

        # Check output report file
        args = 'app.py --basedir tests/fixtures/test-data --manifest .test_manifest.yaml check --report-output tests/fixtures/report.yml'
        sys.argv = args.split()
        cli.main()

        # Assert the file exists
        self.assertTrue(os.path.exists('tests/fixtures/report.yml'))


        # attempt to load the File
        with open('tests/fixtures/report.yml') as report_file:
            report = yaml.safe_load(report_file.read())
            self.assertTrue('changed' in report)
            self.assertTrue('added' in report)
            self.assertTrue('removed' in report)

    def tearDown(self):
        """ Common tearDown tasks for all tests in this test case """

        if os.path.exists('.test_manifest.yaml'):
            os.unlink('.test_manifest.yaml')
        if os.path.exists('tests/fixtures/test-data/test-file'):
            os.unlink('tests/fixtures/test-data/test-file')
        if os.path.exists('tests/fixtures/report.yml'):
            os.unlink('tests/fixtures/report.yml')

if __name__ == '__main__':
    unittest.main()
