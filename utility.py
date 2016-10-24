#!/usr/bin/python3
# -*- coding: utf-8 -*-
import errno
import getpass
import os
import time


def getuser():
    return getpass.getuser()


def getfiledatetime(filepath, datetimetype):
    # created date = 0
    # modified date = 1
    if datetimetype == 0:
        d = os.path.getctime(filepath)
    else:
        d = os.path.getmtime(filepath)
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d))


def getcurrenttime():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def path_from_filepath(filepath):
    return os.path.dirname(filepath)


def file_from_filepath(filepath):
    return os.path.basename(filepath)


def pathexists(path, makedirectory=False):
    if not os.path.exists(path) and makedirectory is True:
        createpath(path)
    return os.path.exists(path)


def fileexists(path):
    if not os.path.isfile(path):
        return "The file '" + path + "' does not exist."


def createpath(filepath):
    try:
        os.makedirs(filepath)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def get_ordinal_position(num):
    ordinal = lambda num: '%d%s' % (
        num, {11: 'th', 12: 'th', 13: 'th'}.get(num % 100, {1: 'st', 2: 'nd', 3: 'rd', }.get(num % 10, 'th')))
    return ordinal(num)
