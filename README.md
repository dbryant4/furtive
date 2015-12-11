Furtive
=======

[![Build Status](https://travis-ci.org/dbryant4/furtive.svg?branch=master)](https://travis-ci.org/dbryant4/furtive)

File Integrity Verification (furtive) aims to ensure long term data integrity verification for digital archival purposes. The idea is to create a manifest, or hash list, of all the files of which you wish to confirm integrity. Once a manifest has been created, a user can then confirm the integrity of files at any point in the future.

The documentation is available on Read The Docs at [furtive.readthedocs.org](https://furtive.readthedocs.org/)

Contents
--------
* [Home](index.md)
* [API Reference](api_ref.md)

## Requirements

- Python 2.7


## Getting Started

To install furtive, run `python setup.py install`.

## CLI Usage

Suppose you have a million digital photos in a directory called `my-photos` that you have taken over the years.

To record the current state of the files, run `furtive --basedir my-photos create`

This command creates the file `.manifest.yaml` in the `my-photos/` directory. The location and name of this file can be changed by using the `--manifest` argument.

At this point, you can be sure that you will know if a file has changed. To check the files on the file system to the manifest, run `furtive --basedir my-photos compare`. The application will output a list of files which have been added, removed, or changed. This output is YAML format so it should be easy to parse.

## Tests

This application comes with tests. To run them, ensure you have `tox` installed (`pip install tox`). Then you can run `tox` to run the tests.

To build the docs, run `tox -e docs`

## Licensing

LGPL
