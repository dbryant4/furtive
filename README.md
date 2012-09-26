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

To hash and update
python hashDir.py --manifest ~/test.manifest --update-manifest

Furtive Module Usage:
fur = Furtive('/path/to/base/dir')
fur.setManifest('/path/to/optional/external/manifest') # Optional defaults to ./.manifest/db
fur.compare() # Tell Furtive to hash the files in the provided dir and then compare them with the previous hashes
fur.hashes    # Dict of files and hashes [{'relative/path/to/file': 'hash'}]
fur.add       # list containing newly added files
fur.removed   # list containing files that have been removed
fur.unchanged # list containing unchanged files (hopefully all files)
fur.changed   # list containing changed files (ie hash values are different)
fur.getPreviousHash('file') #get the previous hash of file (equivelant to fur.hashes['file'])
fur.updateManifest()  # Write changes to manifest

ToDo
======
 - Test to see if manifest file exists before opening to prevent creating new manifest file even when we are not testing
 - Optimize for large amounts of data. Currently stores all hashes in a data type then returns the hashes. 
 - Improve documentation by complying with PEP8
 - Add options for using multiple hash algorithms
     - Add arg options for users to select which hash to use
     - Automatically detect previous hashes used in existing manifests 
 - Update manifest database instead of deleting everything
 - Add functionality to store previous hashes along with date
 - Import sha1sum output into manifest
