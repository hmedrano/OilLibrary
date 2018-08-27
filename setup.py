#!/usr/bin/env python
import os
import sys
import fnmatch
import shutil

from setuptools import setup, find_packages
from distutils.command.clean import clean

from setuptools import Command
from setuptools.command.build_py import build_py
from setuptools.command.test import test as TestCommand

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
pkg_name = 'oil_library'
pkg_version = '1.0.6'

db_init_script_name = 'initialize_OilLibrary_db'


def clean_files(del_db=False):
    src = os.path.join(here, r'oil_library')

    to_rm = []
    for root, _dirnames, filenames in os.walk(src):
        for filename in fnmatch.filter(filenames, '*.pyc'):
            to_rm.append(os.path.join(root, filename))

    to_rm.extend([os.path.join(here, '{0}.egg-info'.format(pkg_name)),
                  os.path.join(here, 'build'),
                  os.path.join(here, 'dist')])
    if del_db:
        to_rm.extend([os.path.join(src, 'OilLib.db')])

    for f in to_rm:
        try:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(f)
        except Exception:
            pass

        print ("Deleting {0} ..".format(f))


def init_db():
    if os.path.exists(os.path.join(here, 'oil_library', 'OilLib.db')):
        print ('OilLibrary database exists - do not remake!')
    else:
        try:
            import oil_library.initializedb
            print ('got this version:', oil_library.__file__)

            print ('calling initializedb.make_db() from the code')
            oil_library.initializedb.make_db()
            print ('OilLibrary database successfully generated from file!')
        except Exception:
            print ('OilLibrary database generation failed')
            raise


class cleanall(clean):
    description = "cleans files generated by 'develop' and SQL lite DB file"

    def run(self):
        clean.run(self)
        clean_files(del_db=True)


class remake_oil_db(Command):
    '''
    Custom command to reconstruct the oil_library database from flat file
    '''
    description = "remake oil_library SQL lite DB from flat file"
    user_options = user_options = []

    def initialize_options(self):
        """init options"""
        pass

    def finalize_options(self):
        """finalize options"""
        pass

    def run(self):
        to_rm = os.path.join(here, r'oil_library', 'OilLib.db')
        try:
            os.remove(to_rm)
        except OSError as e:
            if e.errno == 2:
                pass
            else:
                raise

        print ('Deleting {0} ..'.format(to_rm))
        # ret = call(db_init_script_path())

        print ('****\ncreating a new DB with direct call into package\n********')
        init_db()


class PyTest(TestCommand):
    """So we can run tests with ``setup.py test``"""
    def finalize_options(self):
        TestCommand.finalize_options(self)
        # runs the tests from inside the installed package
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # no idea why it doesn't work to call pytest.main
        # import pytest
        # errno = pytest.main(self.test_args)
        errno = os.system('py.test --pyargs oil_library')
        sys.exit(errno)


class BuildPyCommand(build_py):
    """ Custom build command. """

    def run(self):
        init_db()

        # build_py is an old-style class, so we can't use super()
        build_py.run(self)


s = setup(name=pkg_name,
          version=pkg_version,
          description=('{}: {}'.format(pkg_name,
                                       'The NOAA library of oils '
                                       'and their properties.')),
          long_description=README,
          author='ADIOS/GNOME team at NOAA ORR',
          author_email='orr.gnome@noaa.gov',
          url='',
          keywords='adios weathering oilspill modeling',
          packages=find_packages(),
          include_package_data=True,
          package_data={'oil_library': ['OilLib.db',
                                        'OilLib',
                                        'OilLibTest',
                                        'OilLibNorway',
                                        'blacklist_whitelist.txt',
                                        'tests/*.py',
                                        'tests/sample_data/*']},
          cmdclass={'remake_oil_db': remake_oil_db,
                    'cleanall': cleanall,
                    'test': PyTest,
                    'build_py': BuildPyCommand,
                    },
          entry_points={'console_scripts': [('{} = oil_library.initializedb'
                                             ':make_db'
                                             .format(db_init_script_name)),
                                            ('diff_import_files = '
                                             'oil_library.scripts.oil_import'
                                             ':diff_import_files_cmd'),
                                            ('add_header_to_import_file = '
                                             'oil_library.scripts.oil_import'
                                             ':add_header_to_csv_cmd'),
                                            ],
                        },
          zip_safe=False,
          )


if 'develop' in s.script_args and '--uninstall' not in s.script_args:
    init_db()
