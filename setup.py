#!/usr/bin/env python

from distutils.core import setup

setup(name='Furtive',
      version='0.2',
      description='File Integrity Verification System',
      author='Derrick Bryant',
      author_email='dbryant4@gmail.com',
      packages=['furtive'],
      scripts=['scripts/furtive'],
      install_requires=[
        'PyYAML==3.11',
        'argparse==1.4.0'
      ]
     )
