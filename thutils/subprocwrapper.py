# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''


import logging
import os
import subprocess

import dataproperty
from thutils.logger import logger


class SubprocessWrapper(object):

    @property
    def dry_run(self):
        return self.__dry_run

    def __init__(self, dry_run=False):
        self.__dry_run = dry_run
        self.is_show_timestamp = False
        self.command_log_level = logging.DEBUG

    def __show_command(self, command):
        import datetime

        log_level = logging.getLogger('').getEffectiveLevel()

        if log_level == logging.NOTSET:
            return

        if self.is_show_timestamp:
            output = str(datetime.datetime.now()) + ": " + command
        else:
            output = command

        if self.command_log_level == logging.INFO:
            logger.info(output)
        elif self.command_log_level == logging.DEBUG:
            logger.debug(output)

    def run(self, command, ignore_error_list=()):
        import re
        import thutils.common as common

        if dataproperty.is_empty_string(command):
            raise ValueError("null command")

        self.__show_command(command)
        if self.dry_run:
            return 0

        if re.search("\(.*\)", command) is None:
            if not common.is_install_command(command.split()[0]):
                raise RuntimeError("command not found: " + command)

        tmp_environ = dict(os.environ)
        tmp_environ["LC_ALL"] = "C"

        proc = subprocess.Popen(command, shell=True, env=tmp_environ)
        _ret_stdout, _ret_stderr = proc.communicate()
        return_code = proc.returncode

        if return_code != 0:
            if all([
                dataproperty.is_not_empty_list_or_tuple(ignore_error_list),
                return_code not in ignore_error_list
            ]):
                logger.error("failed '%s' = %d" % (command, return_code))
            else:
                logger.debug(
                    "return code of '%s' = %d" % (command, return_code))

        return return_code

    def popen_command(self, command, std_in=None, environ=None):
        self.__show_command(command)
        if self.dry_run:
            return None

        if environ is not None:
            tmp_environ = environ
        else:
            tmp_environ = dict(os.environ)
            tmp_environ["LC_ALL"] = "C"

        process = subprocess.Popen(
            command, env=tmp_environ, shell=True,
            stdin=std_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logger.debug(
            "Popen: command=%s, pid=%d" % (command, process.pid))

        return process
