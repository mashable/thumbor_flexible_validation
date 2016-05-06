#!/usr/bin/python
# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/globocom/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com timehome@corp.globo.com

from setuptools import setup
from setuptools import find_packages

setup(
    name='thumbor_proxy',
    version='1.0.1',
    packages=find_packages(),
    install_requires=[
        'thumbor',
    ],
    tests_require = ['thumbor', 'scikit-image', 'preggy', 'nosetest', 'numpy', 'PIL']
)
