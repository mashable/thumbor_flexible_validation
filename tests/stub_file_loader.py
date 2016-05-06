#!/usr/bin/python
# -*- coding: utf-8 -*-

from thumbor.loaders import LoaderResult
from datetime import datetime
from os import fstat
from os.path import join, exists, abspath, dirname
from tornado.concurrent import return_future

@return_future
def load(context, path, callback):
    file_path = abspath(join(dirname(__file__), "fixtures/images/image.jpg"))
    result = LoaderResult()
    if exists(file_path):
        with open(file_path, 'r') as f:
            stats = fstat(f.fileno())

            result.successful = True
            result.buffer = f.read()

            result.metadata.update(
                size=stats.st_size,
                updated_at=datetime.utcfromtimestamp(stats.st_mtime)
            )
    else:
        result.error = LoaderResult.ERROR_NOT_FOUND
        result.successful = False

    callback(result)