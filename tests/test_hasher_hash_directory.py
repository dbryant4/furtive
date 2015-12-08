""" Test cases for furtive.hasher object """

import logging
import unittest

from furtive.hasher import HashDirectory, hash_task

class TestHashDirectory(unittest.TestCase):
    def test_hash_directory(self):
        """ Ensure HashDirectory will correctly hash all files in a directory """

        logging.basicConfig(level=logging.DEBUG)

        hash_directory = HashDirectory('test-data')

        results = hash_directory.hash_files()

        self.assertEqual(results['documents/Important Document 1.odt'], 'd460a36805fb460c038d96723f206b20')
        self.assertEqual(results['documents/Important Presentation.odp'], '1911ec839cedcbf00739a7d3447ec3a3')
        self.assertEqual(results['pictures/Picture #1.jpg'], '6eec850e32622c0e33bdae08ced29e24')
        self.assertEqual(results['documents/exclude_me.txt'], '2e7d8cb32bb82e838506aff5600182d1')
        self.assertEqual(len(results), 4)


    def test_hash_task(self):
        """ Ensure furtive.hasher.hash_task works as expected """

        result = hash_task('test-data/documents/Important Document 1.odt')
        self.assertEqual(result['test-data/documents/Important Document 1.odt'], 'd460a36805fb460c038d96723f206b20', msg=result)

if __name__ == '__main__':
    unittest.main()
