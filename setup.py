import os
from setuptools import setup
import parmatter

with open('README.rst','w') as f:
    f.write(parmatter.__doc__)

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    with open(fname) as f:
        return f.read()

setup(
    name = 'candemaker',
    version = '0.0.1',
    author = 'Rick Teachey',
    author_email = 'rickteachey@cbceng.com',
    description = ('Tools for parsable formatters (with unformat() capability).'),
    keywords = 'string Formatter parse',
    url = 'cbceng.com',
    py_modules=['parmatter','test_parmatter'],
    packages=[],
    scripts=['scripts/test_script.bat'],
    install_requires=[],
    include_package_data=True,
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        'Topic :: Utilities',
        # 'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Natural Language :: English',
    ],
)