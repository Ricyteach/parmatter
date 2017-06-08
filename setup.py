#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()

setup(
    name = 'parmatter',
    version = '0.0.3',
	url='https://github.com/Ricyteach/parmatter',
    author = 'Rick Teachey',
    author_email = 'ricky@teachey.org',
    description = ('Tools for formatters that can also parse strings (i.e., with `unformat()` capability): a.k.a., "parmatters".'),
	license = 'BSD',
    keywords = 'string Formatter format parse unformat parmatter format_group linemaker',
    py_modules=['src/parmatter/parmatter','src/parmatter/utilities'],
 	package_dir={'':'src'},
    packages=find_packages('src', exclude=['*.tests', '*.tests.*', 'tests.*', 'tests']),
    scripts=['scripts/test_script.bat'],
    install_requires=['parse'],
    include_package_data=True,
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Text Processing',
        'Topic :: Utilities',    ],
)