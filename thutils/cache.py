# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

import datetime
import os
import sys

import thutils
from thutils.logger import logger


class memoize:

    def __init__(self, function):
        self.function = function
        self.memoized = {}

    def __call__(self, *args):
        try:
            return self.memoized[args]
        except KeyError:
            self.memoized[args] = self.function(*args)
            return self.memoized[args]


class CommandCache:

    __CACHE_ROOT_DIR = "/tmp/__thutils__"

    cache_lifetime_sec = 0

    @classmethod
    def initialize(cls):
        cls.__sys_wrapper = thutils.subprocwrapper.SubprocessWrapper()

    @classmethod
    def clear(cls):
        cache_dir_path = cls.__get_command_cache_store_dir()

        try:
            import shutil

            if os.path.isdir(cache_dir_path):
                shutil.rmtree(cache_dir_path, False)
        except (OSError, os.error):
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return False

        return True

    @classmethod
    def execute(cls, command, suffix=""):
        import thutils.common as common

        cache_dir_path = cls.__get_command_cache_store_dir()
        output_cache_path = os.path.join(
            cache_dir_path,
            common.command_to_filename(command, suffix) + ".txt")

        if os.path.exists(output_cache_path):
            if cls.__is_cache_expire(output_cache_path):
                logger.debug(
                    "cache miss: cache lifetime expired: %s" % (output_cache_path))
            else:
                logger.debug("cache hit: " + output_cache_path)
                return output_cache_path
        else:
            logger.debug("cache miss: " + output_cache_path)

        collect_command = "%s > %s 2>&1" % (command, output_cache_path)
        cls.__sys_wrapper.run(collect_command, ignore_error_list=None)

        return output_cache_path

    @classmethod
    def __get_command_cache_store_dir(cls):
        cache_dir_path = os.path.join(
            cls.__CACHE_ROOT_DIR, "__thutils_command_cache__")

        thutils.gfile.FileManager.make_directory(cache_dir_path, force=True)

        return cache_dir_path

    @classmethod
    def __is_cache_expire(cls, cache_file_path):
        last_modified = datetime.datetime.fromtimestamp(
            os.stat(cache_file_path).st_mtime)
        dt = datetime.datetime.now() - last_modified
        diff_seconds = (
            dt.seconds + dt.days *
            thutils.gtime.getTimeUnitSecondsCoefficient("d"))

        return diff_seconds > cls.cache_lifetime_sec
