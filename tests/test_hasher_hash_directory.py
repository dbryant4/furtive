""" Test cases for furtive.hasher object """

import logging
import unittest
import multiprocessing

from mock import MagicMock, patch

from furtive.hasher import HashDirectory, hash_task, initializer

class TestHashDirectory(unittest.TestCase):
    def test_hash_directory(self):
        """ Ensure HashDirectory will correctly hash all files in a directory """

        hash_directory = HashDirectory('tests/fixtures/test-data')

        results = hash_directory.hash_files()

        self.assertEqual(results['documents/Important Document 1.odt'], 'd460a36805fb460c038d96723f206b20')
        self.assertEqual(results['documents/Important Presentation.odp'], '1911ec839cedcbf00739a7d3447ec3a3')
        self.assertEqual(results['pictures/Picture #1.jpg'], '6eec850e32622c0e33bdae08ced29e24')
        self.assertEqual(results['documents/exclude_me.txt'], '2e7d8cb32bb82e838506aff5600182d1')
        self.assertEqual(len(results), 4)

    def test_hash_directory_keyboard_interupt(self):
        """ Ensure HashDirectory gracefully handles a KeyboardInterrupt """

        with patch('furtive.hasher.multiprocessing.Pool') as mock_pool:
            pool = MagicMock()
            pool.map.side_effect = KeyboardInterrupt
            mock_pool.return_value = pool

            hash_directory = HashDirectory('tests/fixtures/test-data')
            results = hash_directory.hash_files()

            pool.terminate.assert_called_once_with()
            self.assertEqual(results, {})

    def test_hash_task(self):
        """ Ensure furtive.hasher.hash_task works as expected """

        terminating = MagicMock()
        terminating.is_set.return_value = False
        initializer(terminating)

        result = hash_task('tests/fixtures/test-data/documents/Important Document 1.odt')
        self.assertEqual(result['tests/fixtures/test-data/documents/Important Document 1.odt'], 'd460a36805fb460c038d96723f206b20', msg=result)

    def test_hash_task_terminates(self):
        """ Ensure furtive.hasher.hash_task terminates when terminating is set """

        terminating = MagicMock()
        terminating.is_set.return_value = True
        initializer(terminating)

        result = hash_task('tests/fixtures/test-data/documents/Important Document 1.odt')
        self.assertEqual(result, None, msg=result)

    def test_hash_task_keyboard_interupt(self):
        """ Ensure furtive.hasher.hash_task sets terminating to true during KeyboardInterrupt """

        terminating = MagicMock(spec=multiprocessing.Event())
        terminating.is_set.side_effect = KeyboardInterrupt
        initializer(terminating)

        result = hash_task('tests/fixtures/test-data/documents/Important Document 1.odt')

        self.assertEqual(result, None)
        terminating.set.assert_called_once_with()

if __name__ == '__main__':
    unittest.main()
