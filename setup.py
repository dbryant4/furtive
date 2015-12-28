#!/usr/bin/env python

from distutils.core import setup

__VERSION__ = '0.4.0'

long_description = """
Github: https://github.com/dbryant4/furtive
"""

setup(name='Furtive',
      version=__VERSION__,
      description='File Integrity Verification System',
      author='Derrick Bryant',
      author_email='dbryant4@gmail.com',
      long_description=long_description,
      license='MIT',
      packages=['furtive'],
      entry_points={
        'console_scripts': [
            'furtive=furtive.cli:main',
        ]
      },
      url='https://furtive.readthedocs.org',
      download_url='https://github.com/dbryant4/furtive',
      install_requires=[
        'PyYAML==3.11',
        'argparse==1.4.0',
        'future==0.15.2'
      ],
      classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
      ],
     )
