#!/usr/bin/env python
import io
from os import path
from setuptools import setup, find_packages

from pywind import __version__

# Get the long description from the relevant file
here = path.abspath(path.dirname(__file__))
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='pywind',
    version=__version__,
    description='Python Modules to access online information relating to renewable energy in the UK',
    long_description=long_description,
    author='David Reid',
    author_email='zathrasorama@gmail.com',
    url='https://github.com/zathras777/pywind',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'lxml', 'xlrd', 'html5lib'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    license='Unlicense',
)
