#!/usr/bin/env python
import io
from os import path
from setuptools import setup, find_packages

from pywind import __version__

# Get the long description from the relevant file
here = path.abspath(path.dirname(__file__))
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


with io.open(path.join(here, 'requirements.txt')) as rfh:
    requires = [line.strip() for line in rfh.readlines()]


setup(
    name='pywind',
    version=__version__,
    description='Python Modules to access online information relating to renewable energy in the UK',
    long_description=long_description,
    author='David Reid',
    author_email='zathrasorama@gmail.com',
    url='https://github.com/zathras777/pywind',
    packages=find_packages(exclude=['tests', 'sample_scripts']),
    install_requires=requires,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': ['pywind=pywind.command_line:main']
    },

    test_suite='tests',
    license='Unlicense',
)
