'''
@author: Tsuyoshi Hombashi
'''

import os
import logging
import subprocess

from thutils.logger import logger


class SystemWrapper(object):

    @property
    def dry_run(self):
        return self.__dry_run

    def __init__(self, dry_run=False):
        self.__dry_run = dry_run		# Boolean
        self.is_show_timestamp = False
        self.command_log_level = logging.DEBUG

        if dry_run:
            logger.info("dry run")

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
        else:
            # no output
            pass

    def run(self, command, ignore_error_list=()):
        import re
        import thutils.common as common

        if common.isEmptyString(command):
            logger.error("null command")
            return -1

        self.__show_command(command)
        if self.__dry_run:
            return 0

        if re.search("\(.*\)", command) is None:
            if not common.is_install_command(command.split()[0]):
                logger.error("command not found: " + command)
                return -1

        tmp_environ = dict(os.environ)
        tmp_environ["LC_ALL"] = "C"

        proc = subprocess.Popen(command, shell=True, env=tmp_environ)
        # proc	= subprocess.Popen(command, shell=True, env=tmp_environ,
        #			stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_code = proc.wait()

        #_ret_stdout, _ret_stderr	= proc.communicate()
        #return_code	= proc.returncode

        if not common.isEmptyList(ignore_error_list):
            if return_code != 0 and return_code not in ignore_error_list:
                logger.error("failed '%s' = %d" % (command, return_code))

        if return_code != 0:
            logger.debug(
                "return code of '%s' = %d" % (command, return_code))

        return return_code

    def call(self, command_list):
        self.__show_command(" ".join(command_list))
        if self.__dry_run:
            return 0

        return subprocess.check_call(command_list)

    def popenCommand(self, command, std_in=None, environ=None):
        self.__show_command(command)
        if self.__dry_run:
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
