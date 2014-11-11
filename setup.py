#!/usr/bin/env python

from distutils.core import setup

setup(
    name='pywind',
    version='0.9.2',
    description='Python Modules to access online information relating to wind energy in the UK',
    author='David Reid, fixes by Andrew Smith',
    author_email='zathrasorama@gmail.com',
    url='http://github.com/energynumbers/pywind/',
    packages=['pywind',
              'pywind.ofgem',
              'pywind.bmreports',
              'pywind.roc',
              'pywind.decc'],
    requires=['lxml','xlrd','html5lib','requests','future','xlwt_future']
)
