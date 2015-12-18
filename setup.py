#!/usr/bin/env python

from distutils.core import setup

__VERSION__ = '0.2.0'

long_description = "See https://furtive.readthedocs.org"

setup(name='Furtive',
      version=__VERSION__,
      description='File Integrity Verification System',
      author='Derrick Bryant',
      author_email='dbryant4@gmail.com',
      long_description=long_description,
      packages=['furtive'],
      scripts=['scripts/furtive'],
      url='https://furtive.readthedocs.org',
      install_requires=[
        'PyYAML==3.11',
        'argparse==1.4.0'
      ]
     )
