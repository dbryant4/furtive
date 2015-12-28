Furtive
=======

[![Build Status](https://travis-ci.org/dbryant4/furtive.svg?branch=master)](https://travis-ci.org/dbryant4/furtive)
[![Code Climate](https://codeclimate.com/github/dbryant4/furtive/badges/gpa.svg)](https://codeclimate.com/github/dbryant4/furtive)
[![codecov.io](https://codecov.io/github/dbryant4/furtive/coverage.svg?branch=master)](https://codecov.io/github/dbryant4/furtive?branch=master)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/087831a7ac124904b9e291503ef43a37/badge.svg)](https://www.quantifiedcode.com/app/project/087831a7ac124904b9e291503ef43a37)

File Integrity Verification (furtive) aims to ensure long term data integrity verification for digital archival purposes. The idea is to create a manifest, or hash list, of all the files of which you wish to confirm integrity. Once a manifest has been created, a user can then confirm the integrity of files at any point in the future.

The documentation is available on Read The Docs at [furtive.readthedocs.org](https://furtive.readthedocs.org/)

Contents
--------
* [Home](index.md)
* [CLI Reference](cli_ref.md)
* [API Reference](api_ref.md)

## Requirements

- Python 2.7 or 3.5


## Getting Started

To install furtive, run `pip install furtive`.

## CLI Usage

See the [CLI Reference](cli_ref.md) for more information about available command line arguments.

### Use Case Example
Suppose you have a million digital photos in a directory called `my-photos` that you have taken over the years. You would like to know if the files begin to decay due to hardware failure or something else. Alternatively, you may wish to have reassurance that your photos have not become corrupted while being stored in a cloud backup solution such as S3 or Glacier.

To record the current state of the files, run `furtive --basedir my-photos create`

This command creates the file `.manifest.yaml` in the `my-photos/` directory. The location and name of this file can be changed by using the `--manifest` argument.

At this point, you can be sure that you will know if a file has changed. To check the files on the file system to the recorded state in the manifest, run `furtive --basedir my-photos check`. The application will output a list of files which have been added, removed, or changed. This output is YAML format so it should be easy to parse. Additionally, furtive will exit with 1 indicating the check failed. This command can be placed in a cron job and setup to send a notification if a file has changed.

### Actions

There are a few actions which can be performed by furtive.

- **create** - create a new manifest from the files in the directory specified by the `--basedir` argument.

- **compare** - compare the current state of the files on the file system with the recorded state in the manifest file. A YAML based report will be created detailing which files have changed and which files have been added or removed. Status code is 0 if the comparison was successful.

- **check** - check the integrity of files listed in the manifest. Same as `compare` but exits with status code 1 if there are changes to the files included in the manifest. That is, if any file hash changes or if files are added or removed, the application will exit with a status code of 1 to indicate there are changes. This action can be useful for scripting. For example, to run a nightly cron check of a manifest. A YAML based report will be generated as well.

## Tests

This application comes with tests. To run them, ensure you have `tox` installed (`pip install tox`). Then you can run `tox` to run the tests.

To build the docs, run `tox -e docs`. The HTML docs will be generated in the `.tox/docs/tmp/html/` directory.

## Faster YAML

By default, furtive will install and use the full Python implementation of the YAML parser which is very slow. In a testing environment, the Python implementation of the YAML loader took 1 minute to parse a 187,000 line furtive manifest file. By contrast, when the [LibYaml](http://pyyaml.org/wiki/LibYAML) parser was used, the loader took only 5 seconds to parse the same file.

To install the faster parser, perform the following steps:

1. Follow the [instructions from the LibYaml website](http://pyyaml.org/wiki/LibYAML) to download and install the latest release of libyaml.
2. Reinstall the PyYAML package by downloading the latest tar from the [PyYAML website](http://pyyaml.org/wiki/PyYAMLDocumentation) and running `python setup.py --with-libyaml install`
