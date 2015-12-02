""" Test cases for HashTask object """

import unittest

from furtive.hasher import HashTask

class TestHashTask(unittest.TestCase):

    def test_hash_task(self):
        """ Ensure HashTask will correctly hash a file and return the result """

        hash_task = HashTask('test-data/documents/Important Document 1.odt')
        hash_task.__call__()

        self.assertEqual(hash_task.hash, 'd460a36805fb460c038d96723f206b20')
        self.assertEqual(str(hash_task), 'd460a36805fb460c038d96723f206b20')
        self.assertFalse(str(hash_task) == 'NOT_A_REAL_HASH')

if __name__ == '__main__':
    unittest.main()
