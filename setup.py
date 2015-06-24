#!/usr/bin/env python

from setuptools import setup, find_packages
from pywind import __version__

setup(
    name='pywind',
    version=__version__,
    description='Python Modules to access online information relating to wind energy in the UK',
    author='David Reid',
    author_email='zathrasorama@gmail.com',
    url='https://github.com/zathras777/pywind',
    packages=find_packages(exclude=['tests']),
    requires=['lxml', 'xlrd', 'html5lib'],
    test_suite='tests'
)
