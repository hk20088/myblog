#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Leon Hu'

'''
JSON API definition
'''

# import json
# import logging
# import inspect
# import functools


# 简单的几个api错误异常类，用于跑出异常


class APIError(Exception):

    """the base APIError which contains error(required), data(optional) and message(optional). """
    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


class APIValueError(APIError):
    """docstring for APIValueError"""

    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)


class APIResourceNotFoundError(APIError):
    """docstring for APIResourceNotFoundError"""

    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)


class APIPermissionError(object):
    """docstring for APIPermissionError"""

    def __init__(self, message=''):
        super(APIPermissionError, self).__init__( 'permission:forbidden', 'permission', message)
