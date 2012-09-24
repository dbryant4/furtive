Furtive
=======

File Integrity Verification System (furtive) aims to ensure long term data integrity verification for digital archival purposes.

Example Usage
======

There is a script which shows how to utilize the Furtive Python module called hashDir.py. 

For help:
python hashDir.py --help

Simple usage that does not save hash data:
python hashDir.py --update-manifest --dir /path/to/archived/data

Simple usage to print out a report of files that have been add, removed, changed, and unchanged. Useful for a test :
python hashDir.py --dir /path/to/archived/data

To has
python hashDir.py --manifest ~/test.manifest --update-manifest

ToDo
======
 - Optimize for large amounts of data. Currently stores all hashes in a data type then returns the hashes. 
 - Improve documentation by complying with PEP8
 - Add options for using multiple hash algorithms
     - Add arg options for users to select which hash to use
     - Automatically detect previous hashes used in existing manifests 
 - Update manifest database instead of deleting everything
 - Add functionality to store previous hashes along with date