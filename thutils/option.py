'''
@author: Tsuyoshi Hombashi
'''

import six

import thutils.common as common
from thutils.logger import logger


TN_ExecuteOption = "Execute Option"


def createExecuteOptionTable(con, options):
    import os.path
    import sys

    con.checkAccessPermission(["w", "a"])

    table_name = TN_ExecuteOption
    if con.hasTable(table_name):
        logger.debug("'%s' table already exists" % (table_name))
        return True

    value_listlist = [
        ["command option", " ".join(sys.argv[1:])],
    ]

    for option, value in sorted(six.iteritems(options.__dict__)):
        value = str(value)
        if os.path.exists(value):
            value = os.path.realpath(value)

        value_listlist.append([str(option), value])

    return con.create_table_with_data(
        table_name, common.KEY_VALUE_HEADER, value_listlist)


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

    def add_argument_group(self, group_name, title=None, description=None):
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

    def addSqlArgumentGroup(self):
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

        if common.isEmptyListOrTuple(valid_time_format_list):
            logger.error("required at least a valid time format")
            return

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

    """
    def addPlotOption(self):
        import thutils.GGPlotWrapper as plot

        plot_choices = [plot.EXT_PNG, plot.EXT_SVG]

        group = self.add_argument_group("Plot Options")
        group.add_argument(
            "--image-file-format",
            choices=plot_choices, default=plot_choices[0],
            help="image file format: " + " (default=%(default))")
    #"""

    def addSarArgumentGroup(self):
        import thutils.sysstat as sysstat

        help_format = "%s (table = %s)"

        group = self.add_argument_group("Sar Options")
        group.add_argument(
            "-u", action="store_true",
            dest="is_sar_cpu_util", default=False,
            help=help_format % ("CPU utilization.", sysstat.TN_CpuUtil))
        group.add_argument(
            "-b", action="store_true",
            dest="is_sar_block", default=False,
            help=help_format % (
                "I/O and transfer rate statistics.", sysstat.TN_BlockIO))
        group.add_argument(
            "-B", action="store_true",
            dest="is_sar_paging", default=False,
            help=help_format % ("paging statistics.", sysstat.TN_Paging))
        group.add_argument(
            "-c", action="store_true",
            dest="is_sar_task", default=False,
            help=help_format % (
                "task creation activity", sysstat.TN_TaskCreated))
        group.add_argument(
            "-d", action="store_true",
            dest="is_sar_disk", default=False,
            help=help_format % (
                "activity for each block device", sysstat.TN_DiskIO))

        choice_list = ["DEV", "EDEV", "NFS", "NFSD", "SOCK", "ALL"]
        group.add_argument(
            "-n", action="append",
            type=str, choices=choice_list,
            dest="network_arg_list", default=[], metavar="|".join(choice_list),
            help=help_format % (
                "network statistics.",
                sysstat.TN_NetworkFormat % ("|".join(choice_list))))

        group.add_argument(
            "-I", action="store_true",
            dest="is_sar_interrupts", default=False,
            help=help_format % (
                "statistics for a given interrupt.", sysstat.TN_Interrupt))
        group.add_argument(
            "-q", action="store_true",
            dest="is_sar_queue", default=False,
            help=help_format % (
                "queue length and load averages.", sysstat.TN_Queue))
        group.add_argument(
            "-r", action="store_true",
            dest="is_sar_memory_and_swap_util", default=False,
            help=help_format % (
                "memory and swap space utilization statistics.",
                sysstat.TN_MemoryUtil))
        group.add_argument(
            "-R", action="store_true",
            dest="is_sar_memory", default=False,
            help=help_format % ("memory statistics", sysstat.TN_Memory))
        group.add_argument(
            "-v", action="store_true",
            dest="is_sar_inode", default=False,
            help=help_format % (
                "status of inode, file and other kernel tables.",
                sysstat.TN_inode))
        group.add_argument(
            "-w", action="store_true",
            dest="is_sar_system_switching", default=False,
            help=help_format % (
                "system switching activity.", sysstat.TN_SystemSwitch))
        group.add_argument(
            "-W", action="store_true",
            dest="is_sar_swap", default=False,
            help=help_format % ("swapping statistics.", sysstat.TN_Swap))
        group.add_argument(
            "-A", action="store_true",
            dest="is_show_all", default=False, help="all.")

    @staticmethod
    def validate_time_range_option(
            options, valid_time_format_list,
            is_check_time_inversion=True):

        import thutils.gtime as gtime

        options.start_datetime = None
        # if common.isNotEmptyString(options.start_time):
        options.start_datetime = gtime.toDateTimeEx(
            options.start_time, valid_time_format_list)

        options.end_datetime = None
        # if common.isNotEmptyString(options.end_time):
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
            "--with-no-log", action="store_true", default=False,
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

    if hasattr(options, "dry_run") and options.dry_run:
        option_list.append("--dry-run")
    if options.with_no_log:
        option_list.append("--with-no-log")
    if options.log_level == logging.DEBUG:
        option_list.append("--debug")
    if options.log_level == logging.NOTSET:
        option_list.append("--quiet")
    if options.stacktrace:
        option_list.append("--stacktrace")

    return option_list

# sysstat ---


def isAnySarOption(options):
    return any([
        options.is_sar_block,
        options.is_sar_disk,
        len(options.network_arg_list) > 0,
        options.is_sar_interrupts,
        options.is_sar_memory_and_swap_util,
        options.is_sar_queue,
        options.is_sar_inode,
        options.is_sar_swap,
        options.is_sar_paging,
        options.is_sar_task,
        options.is_sar_memory,
        options.is_sar_system_switching,
    ])


def setAllSarOption(options):
    options.is_sar_cpu_util = True
    options.is_sar_block = True
    options.is_sar_disk = True
    options.is_sar_memory_and_swap_util = True
    options.is_sar_memory = True
    options.is_sar_paging = True
    options.is_sar_interrupts = True
    options.is_sar_queue = True
    options.is_sar_inode = True
    options.is_sar_swap = True
    options.is_sar_task = True
    options.is_sar_system_switching = True
    # options.is_show_tty_device	= True
    options.network_arg_list = ["ALL"]


def getDict_TableName_SarOption(options):
    import thutils.sysstat as sysstat

    return {
        sysstat.TN_CpuUtil			: ["-u", options.is_sar_cpu_util],
        sysstat.TN_BlockIO			: ["-b", options.is_sar_block],
        sysstat.TN_Paging			: ["-B", options.is_sar_paging],
        sysstat.TN_TaskCreated		: ["-c", options.is_sar_task],
        sysstat.TN_DiskIO			: ["-d", options.is_sar_disk],
        sysstat.TN_Queue			: ["-q", options.is_sar_queue],
        sysstat.TN_MemoryUtil		: ["-r", options.is_sar_memory_and_swap_util],
        sysstat.TN_Memory			: ["-R", options.is_sar_memory],
        sysstat.TN_inode			: ["-v", options.is_sar_inode],
        sysstat.TN_SystemSwitch		: ["-w", options.is_sar_system_switching],
        sysstat.TN_Swap				: ["-W", options.is_sar_swap],
        sysstat.TN_Interrupt		: ["-I", options.is_sar_interrupts],
        sysstat.TN_NetworkPrefix	: ["-n", len(options.network_arg_list) > 0]
        # TABLE_TtyDevice		: ["-y", options.is_show_tty_device]
    }


def checkSarNetworkOption(parser, options):
    valid_arg_list = ["DEV", "EDEV", "NFS", "NFSD", "SOCK"]

    for n_arg in options.network_arg_list:
        if n_arg not in valid_arg_list and n_arg != "ALL":
            parser.print_help()
            parser.error("-n: invalid option " + n_arg)
        if n_arg == "ALL":
            options.network_arg_list = valid_arg_list
