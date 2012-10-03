Furtive
=======

File Integrity Verification (furtive) aims to ensure long term data integrity verification for digital archival purposes. The idea is to create a manifest, or hash list, of all the files of which you wish to confirm integrity. 

Usage Senario
======
Suppose you have a million digital photos that you have taken over the years. Also suppose you have organized them into a directory structure where the top level directories are the year the pictures under them were taken. For example, a directory named 2006 contains pictures from 2006. On January 1, 2007, you can create a manifest of the 2006 directory using furtive. Then you will be able to confirm the contents of the 2006 directory, and your digital photos, at any point in the future. 

Methods and Variables
======
Furtive Module Usage:
 * fur = new furtive('/path/to/base/dir')
 * fur.set_manifest('/path/to/optional/external/manifest') # Optional defaults to ./.manifest/db
 * fur.compare()   # Tell Furtive to hash the files in the provided dir and then compare them with the previous hashes
 * fur.hashes      # Dict of files and hashes generated using current file contents [{'relative/path/to/file': 'hash'}]
 * fur.prev_hashes  # Dict of files and hashes read from the manifest [{'relative/path/to/file': 'hash'}]
 * fur.add         # list containing newly added files
 * fur.removed     # list containing files that have been removed
 * fur.unchanged   # list containing unchanged files (hopefully all files)
 * fur.changed     # list containing changed files (ie hash values are different)
 * fur.get_previous_hash('file') #get the previous hash of file (equivelant to fur.prevHashes['file'])
 * fur.get_hash('file') #get the previous hash of file (equivelant to fur.hashes['file'])
 * fur.update_manifest()  # Write changes to manifest

Example Usage
======

```
>>> from furtive import furtive
>>> fur = furtive('~/test_dir')
>>> fur.compare()
>>> fur.changed # Shows files that have changed
>>> fur.update_manifest()  # Commits changes to manifest 
```

Example Script
=====
There is a script which shows how to utilize the Furtive Python module called hashDir.py. 

For help:
python hashDir.py --help

Simple usage that does not save hash data:
python hashDir.py --update-manifest --dir /path/to/archived/data

Simple usage to print out a report of files that have been add, removed, and changed. Useful for a nightly email report:
python hashDir.py --dir /path/to/archived/data --report-added -report-removed --report-changed

To hash and update
python hashDir.py --manifest ~/test.manifest --update-manifest
