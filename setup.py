#!/usr/bin/python
# -*- coding: utf-8 -*-

# Custom thumbor app for more flexible URL validation
# https://github.com/mashable/thumbor_proxy

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2016 Mashable

from setuptools import setup
from setuptools import find_packages

setup(
    name='thumbor_flexible_validation',
    version='1.0.1',
    packages=find_packages(),
    install_requires=[
        'thumbor',
    ],
    tests_require = ['thumbor', 'scikit-image', 'preggy', 'nosetest', 'numpy', 'PIL']
)
