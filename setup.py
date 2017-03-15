#!/usr/bin/env python

import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('sqlwhat/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
	name='sqlwhat',
	version=version,
	packages=['sqlwhat'],
	install_requires=['markdown2', 'antlr-plsql', 'antlr-tsql'],
        description = 'Submission correctness tests for sql',
        author = 'Michael Chow',
        author_email = 'michael@datacamp.com',
        url = 'https://github.com/datacamp/sqlwhat')
