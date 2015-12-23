#!/usr/bin/env python
""" furtive command line tool """


import os
import sys
import logging
import argparse

from argparse import RawTextHelpFormatter

import yaml

from furtive import Furtive, __version__


def parse_args(args=None):
    """ Method to parse command line arguments.

        :param args: command line arguments as typed on the command line
        :type args: str

        :return: parsed arguments from argparse()
        :rtype: argparse.Namespace()
    """

    action_help = ''' Which action to perform:
      compare - compare the current state of the files on the file system with
                the recorded state in the manifest file. Status code is 0 if
                the comparison was successful.
      check   - check the integrity of files listed in the manifest. Same as
                compare but exits with status code 1 if there are changes to
                the files included in the manifest. That is, if any file hash
                changes or if files are added or removed, the application will
                exit with a status code of 1 to indicate there are changes.
                This action can be useful for scripting. For example, to run a
                nightly cron check of a manifest.
      create  - create a new manifest from the files inthe directory
                specified by the --basedir argument.
    '''

    parser = argparse.ArgumentParser(description='Manage a Furtive manifest',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('--basedir', action='store', default='.',
                        help='Directory containing files that will be\n'
                             'checked. Default: .')
    parser.add_argument('--manifest', action='store', dest='manifest_path',
                        default=None,
                        help='Location of the manifest file. Manifests may\n'
                             'be located outside the directory indicated by\n'
                             '--basedir. Must provide path and filename of\n'
                             'the manifest file.\n'
                             'Default: <basedir>/.manifest.yaml')
    parser.add_argument('--log-level', action='store', dest='log_level',
                        choices=('debug', 'info', 'warn', 'error', 'critical'),
                        default='info', help='verbosity of furtive')
    parser.add_argument('--exclude', dest='exclude', action='append',
                        default=[], metavar='PATTERN',
                        help='Patterns to exclude files and directories from\n'
                             'manifest. Can have multiple occurances of this\n'
                             'argument. Excludes are not stored in the\n'
                             'manifest so it is up to the user to provide\n'
                             'the same arguments every run. Patterns are\n'
                             'evaluated as UNIX shell-style wildcard\n'
                             'characters. See the [fnmatch documentation]'
                             '(https://docs.python.org/2/library/fnmatch.html)'
                             'for more information.\n\nIt is important to\n'
                             'note that exclusions are not stored. Therefore\n'
                             ',they must be specified for every run of\n'
                             '`furtive`. Otherwise, the files which were\n'
                             'previously excluded will be included and will\n'
                             'show up as files added to the manifest.')
    parser.add_argument('--quiet', action='store_true',
                        help='Only print out critial error messages. Do not\n'
                        'print a report at the end of a compare run. Using\n'
                        'this argument will override the log-level and set\n'
                        'it to "critical". Only acceptions will be printed\n'
                        'to terminal. The return code will be the only way\n'
                        'to know if a Manifest has changed. This is useful\n'
                        'for scripting such as a cron based manifest checks.\n'
                        'Useful with the check command.')
    parser.add_argument('--report-output', metavar='FILE_NAME',
                        type=argparse.FileType('w'), default='-',
                        help='File to print the diff report to. - for stdout.'
                             'This can be consumed by other scripts to'
                             'determine exactly what has changed within the'
                             'manifest'
                             'Default: -')
    parser.add_argument('--version', action='version',
                        version='%(prog)s {version}'
                        .format(version=__version__))
    parser.add_argument('action', choices=('create', 'compare', 'check'),
                        help=action_help,
                        nargs=1)

    if args is None:
        return parser

    parsed_args = parser.parse_args(args)
    parsed_args.action = parsed_args.action.pop()
    if parsed_args.manifest_path is None:
        parsed_args.manifest_path = os.path.join(parsed_args.basedir,
                                                 '.manifest.yaml')
    if parsed_args.quiet:
        parsed_args.log_level = 'critical'

    return parsed_args


def main():
    """ Starting point of the furtive command line tool """

    args = parse_args(sys.argv[1:])

    log_format = '%(asctime)s [%(levelname)s]: %(message)s'
    date_format = '%c %Z'
    numeric_level = getattr(logging, args.log_level.upper(), None)
    logging.basicConfig(level=numeric_level,
                        format=log_format,
                        datefmt=date_format)

    furtive = Furtive(args.basedir, args.manifest_path, args.exclude)

    if args.action == 'create':
        furtive.create()
    elif args.action in ['compare', 'check']:
        changes = furtive.compare()
        if not args.quiet:
            args.report_output.write(yaml.safe_dump(changes,
                                                    default_flow_style=False))
        if args.action == 'check' and (changes['changed'] or
                                       changes['removed'] or
                                       changes['added']):
            sys.exit(1)
