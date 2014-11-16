#!/usr/bin/env python

from distutils.core import setup, Command
from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin
from os import walk, getcwd


class TestCommand(Command):
    description="Run the tests"
    user_options = [ ]

    def initialize_options(self):
        self._dir = getcwd()

    def finalize_options(self):
        pass

    def run(self):
        """
        Finds all the tests modules in tests/, and runs them.
        """
        testfiles = [ ]
        for t in glob(pjoin(self._dir, 'tests', '*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(
                    ['tests', splitext(basename(t))[0]])
                )

        print("\nThese tests require an internet connection and may take a while.\nPlease be patient.\n")
        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity=self.verbose)
        t.run(tests)


setup(
    name='pywind',
    version='0.9.2',
    description='Python Modules to access online information relating to wind energy in the UK',
    author='David Reid',
    author_email='zathrasorama@gmail.com',
    url='http://www.variablepitch.co.uk/pywind/',
    packages=['pywind',
              'pywind.ofgem',
              'pywind.bmreports',
              'pywind.roc',
              'pywind.decc'],
    requires=['lxml','xlrd','html5lib'],
    cmdclass={'test': TestCommand}
)
