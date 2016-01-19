'''
@author: Tsuyoshi Hombashi
'''

import six

import thutils.common as common
from thutils.logger import logger


TN_ExecuteOption = "Execute Option"


class MakeOption:
    MAKE = "make"
    OVERWRITE = "overwrite"
    CLEAN = "clean"
    SKIP = "skip"


class ArgumentParserObject(object):
    """
    wrapper class of argparse
    """

    class GroupName:
        MISC = "Miscellaneous"
        SQL = "SQL"
        TIME_RANGE = "Time Range"

    def __init__(self):
        self.parser = None
        self.dict_group = {}

    def make(self, version, description="", epilog=""):
        import argparse

        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=description, epilog=epilog)
        self.parser.add_argument(
            '--version', action='version', version='%(prog)s ' + version)

        self._add_general_argument_group()
        self._add_log_level_argument_group()

    def parse_args(self):
        return self.parser.parse_args()

    def add_argument_group(self, group_name):
        if common.is_empty_string(group_name):
            raise ValueError("null argument group name")

        group = self.parser.add_argument_group(group_name)
        self.dict_group[group_name] = group

        return group

    def add_dry_run_option(self):
        group = self.dict_group.get(self.GroupName.MISC)
        group.add_argument(
            "--dry-run", action="store_true", default=False,
            help="do no harm.")

    def add_run_option(self):
        group = self.dict_group.get(self.GroupName.MISC)
        group.add_argument(
            "--run", dest="dry_run", action="store_false", default=True,
            help="execute")

    def add_sql_argument_group(self):
        group = self.add_argument_group(self.GroupName.SQL)
        group.add_argument(
            "--sql-logging", action="store_true", default=False,
            help="for debug")

        return group

    def addProfileArgumentGroup(self):
        group = self.add_argument_group("Profile")
        group.add_argument(
            "--profile", action="store_true", default=False,
            help="for execution time profile (python 2.6 or greater required)")

        return group

    def add_time_range_argument_group(
            self, valid_time_format_list,
            start_time_help_msg="", end_time_help_msg=""):

        import re

        if common.is_empty_list_or_tuple(valid_time_format_list):
            raise ValueError("required at least a valid time format")

        # convert datetime format to human readable text
        help_time_format_list = []
        for time_format in valid_time_format_list:
            time_format = re.sub(re.escape("%Y"), "YYYY", time_format)
            time_format = re.sub(re.escape("%y"), "YY", time_format)
            time_format = re.sub(re.escape("%m"), "MM", time_format)
            time_format = re.sub(re.escape("%d"), "DD", time_format)
            time_format = re.sub(re.escape("%H"), "hh", time_format)
            time_format = re.sub(re.escape("%M"), "mm", time_format)
            time_format = re.sub(re.escape("%S"), "ss", time_format)
            help_time_format_list.append(time_format)

        help_text_format = "%s (valid time format: %s)"

        group = self.add_argument_group(self.GroupName.TIME_RANGE)
        group.add_argument(
            "-s", dest="start_time",
            help=help_text_format % (
                start_time_help_msg, " | ".join(help_time_format_list)))
        group.add_argument(
            "-e", dest="end_time",
            help=help_text_format % (
                end_time_help_msg, " | ".join(help_time_format_list)))

        return group

    def addMakeArgumentGroup(self):
        dest = "make_option"

        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            "--clean", dest=dest, action="store_const",
            const=MakeOption.CLEAN, default=MakeOption.MAKE,
            help="remove existing file")
        group.add_argument(
            "--overwrite", dest=dest, action="store_const",
            const=MakeOption.OVERWRITE, default=MakeOption.MAKE,
            help="overwrite existing file")

    @staticmethod
    def validate_time_range_option(
            options, valid_time_format_list,
            is_check_time_inversion=True):

        import thutils.gtime as gtime

        options.start_datetime = gtime.toDateTimeEx(
            options.start_time, valid_time_format_list)
        options.end_datetime = gtime.toDateTimeEx(
            options.end_time, valid_time_format_list)
        options.datetime_range = gtime.DateTimeRange(
            options.start_datetime, options.end_datetime)

        if not is_check_time_inversion:
            return

        try:
            options.datetime_range.verifyTimeRange()
        except TypeError:
            pass

    def _add_general_argument_group(self):
        import logging

        group = self.add_argument_group(self.GroupName.MISC)
        group.add_argument(
            "--time-measure", action="store_const",
            const=logging.INFO, default=logging.DEBUG,
            help="measuring execution time.")
        group.add_argument(
            "--logging", dest="with_no_log", action="store_false", default=True,
            help="suppress output of execution log files.")
        group.add_argument(
            "--stacktrace", action="store_true", default=False,
            help="display stack trace when an error occurred.")

        return group

    def _add_log_level_argument_group(self):
        import logging

        dest = "log_level"

        group = self.parser.add_mutually_exclusive_group()
        group.add_argument(
            "--debug", dest=dest, action="store_const",
            const=logging.DEBUG, default=logging.INFO,
            help="for debug print.")
        group.add_argument(
            "--quiet", dest=dest, action="store_const",
            const=logging.NOTSET, default=logging.INFO,
            help="suppress output of execution log message.")

        return group


def getGeneralOptionList(options):
    import logging

    option_list = []

    try:
        if options.dry_run:
            option_list.append("--dry-run")
    except AttributeError:
        pass
    # if hasattr(options, "dry_run") and options.dry_run:
    #    option_list.append("--dry-run")
    if not options.with_no_log:
        option_list.append("--logging")
    if options.log_level == logging.DEBUG:
        option_list.append("--debug")
    if options.log_level == logging.NOTSET:
        option_list.append("--quiet")
    if options.stacktrace:
        option_list.append("--stacktrace")

    return option_list
