'''
@author: Tsuyoshi Hombashi
'''

import logging

import dataproperty


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
        PROFILE = "Profile"

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
        if dataproperty.is_empty_string(group_name):
            raise ValueError("null argument group name")

        if group_name not in self.dict_group:
            group = self.parser.add_argument_group(group_name)
            self.dict_group[group_name] = group
        else:
            return self.dict_group.get(group_name)

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

    def add_profile_argument_group(self):
        group = self.add_argument_group(self.GroupName.PROFILE)
        group.add_argument(
            "--profile", action="store_true", default=False,
            help="for execution time profile (python 2.6 or greater required)")

        return group

    def add_time_argument_group(self):
        group = self.add_argument_group(self.GroupName.PROFILE)
        group.add_argument(
            "--time-measure", action="store_const",
            const=logging.INFO, default=logging.DEBUG,
            help="measuring execution time.")

        return group

    def add_time_range_argument_group(
            self, start_time_help_msg="", end_time_help_msg=""):

        group = self.add_argument_group(self.GroupName.TIME_RANGE)
        group.add_argument(
            "-s", dest="start_datetime", default=None,
            help=start_time_help_msg)
        group.add_argument(
            "-e", dest="end_datetime", default=None,
            help=end_time_help_msg)

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

    def _add_general_argument_group(self):
        group = self.add_argument_group(self.GroupName.MISC)
        group.add_argument(
            "--logging", dest="with_no_log",
            action="store_false", default=True,
            help="output execution log to a file (%(prog)s.log).")
        group.add_argument(
            "--stacktrace", action="store_true", default=False,
            help="display stack trace when an error occurred.")

        return group

    def _add_log_level_argument_group(self):
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
    option_list = []

    try:
        if options.dry_run:
            option_list.append("--dry-run")
    except AttributeError:
        pass

    if not options.with_no_log:
        option_list.append("--logging")
    if options.log_level == logging.DEBUG:
        option_list.append("--debug")
    if options.log_level == logging.NOTSET:
        option_list.append("--quiet")
    if options.stacktrace:
        option_list.append("--stacktrace")

    return option_list
