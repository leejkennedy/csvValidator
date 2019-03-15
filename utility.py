#!/usr/bin/python3
# -*- coding: utf-8 -*-
import errno
import getpass
import os
import time


def getuser():
    return getpass.getuser()


def get_file_date_time(file_path, date_time_type):
    # created date = 0
    # modified date = 1
    if date_time_type == 0:
        d = os.path.getctime(file_path)
    else:
        d = os.path.getmtime(file_path)
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(d))


def get_current_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


def path_from_file_path(file_path):
    return os.path.dirname(file_path)


def file_from_file_path(file_path):
    return os.path.basename(file_path)


def path_exists(path, make_directory=False):
    if not os.path.exists(path) and make_directory is True:
        create_path(path)
    return os.path.exists(path)


def file_exists(path):
    if not os.path.isfile(path):
        return "The file '" + path + "' does not exist."


def create_path(filepath):
    try:
        os.makedirs(filepath)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def get_ordinal(num):
    ordinal = str(num)
    if num > 0:
        ordinal = ordinal + (lambda num_o:
                             ({11: 'th', 12: 'th', 13: 'th'}.get(num % 100,
                                                                 {1: 'st', 2: 'nd', 3: 'rd', }.get(num % 10, 'th'))))(
            num)
    return ordinal
