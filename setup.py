#!/usr/bin/env python

from distutils.core import setup

setup(name='pywind',
      version='0.2.2',
      description='Python Modules to access online information relating to wind energy in the UK',
      author='David Reid',
      author_email='zathrasorama@gmail.com',
      url='http://www.variablepitch.co.uk/pywind/',
      packages=['pywind', 'pywind.bmreports','pywind.ofgem'],
     )
