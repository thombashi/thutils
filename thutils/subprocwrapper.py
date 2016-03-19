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

    @property
    def command(self):
        return self.__command

    @property
    def stdout_text(self):
        return self.__stdout_text

    @property
    def stderr_text(self):
        return self.__stderr_text

    def __init__(self, dry_run=False):
        self.__dry_run = dry_run
        self.is_show_timestamp = False
        self.command_log_level = logging.DEBUG

        self.__command = None
        self.__stdout_text = None
        self.__stderr_text = None

    def __get_env(self, env=None):
        import platform

        if env is not None:
            return env

        if platform.system() == "Linux":
            return dict(os.environ, LC_ALL="C")

        return os.environ

    def __show_command(self):
        import datetime

        log_level = logging.getLogger('').getEffectiveLevel()

        if log_level == logging.NOTSET:
            return

        if self.is_show_timestamp:
            output = str(datetime.datetime.now()) + ": " + self.command
        else:
            output = self.command

        if self.command_log_level == logging.INFO:
            logger.info(output)
        elif self.command_log_level == logging.DEBUG:
            logger.debug(output)

    def __validate_command(self):
        import re
        import thutils.common as common

        if dataproperty.is_empty_string(self.command):
            raise ValueError("null command")

        if re.search("\(.*\)", self.command) is None:
            if not common.is_install_command(self.command.split()[0]):
                raise RuntimeError("command not found: " + self.command)

    def run(self, command, ignore_error_list=()):
        self.__command = command
        self.__validate_command()
        self.__show_command()
        if self.dry_run:
            return 0

        proc = subprocess.Popen(
            command, shell=True, env=self.__get_env(),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.__stdout_text, self.__stderr_text = proc.communicate()
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
        self.__command = command
        self.__validate_command()
        self.__show_command()
        if self.dry_run:
            return None

        process = subprocess.Popen(
            command, env=self.__get_env(environ), shell=True,
            stdin=std_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logger.debug(
            "Popen: command=%s, pid=%d" % (command, process.pid))

        return process
