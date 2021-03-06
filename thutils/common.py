# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

from __future__ import with_statement
import os.path
import pathvalidate
import re
import sys

import dataproperty
import six


def safe_division(dividend, divisor):
    """
    :return:
        nan: invalid arguments
    :rtype: float
    """

    try:
        divisor = float(divisor)
        dividend = float(dividend)
    except (TypeError, ValueError, AssertionError):
        return float("nan")

    try:
        return dividend / divisor
    except (ZeroDivisionError):
        return float("nan")


def removeItemFromList(item_list, item):
    is_remove = False
    if item in item_list:
        item_list.remove(item)
        is_remove = True

    return is_remove


def removeListFromList(input_list, remove_list):
    for remove_item in remove_list:
        removeItemFromList(input_list, remove_item)


def diffItemList(item_list, remove_list):
    # return list(set(item_list).difference(set(remove_list)))
    work_list = list(item_list)
    for remove_item in remove_list:
        removeItemFromList(work_list, remove_item)

    return work_list


def _get_unit(byte):
    kilo = 1024

    unit_pair_list = [
        [kilo ** 5, "PB"],
        [kilo ** 4, "TB"],
        [kilo ** 3, "GB"],
        [kilo ** 2, "MB"],
        [kilo ** 1, "KB"],
    ]

    for unit_pair in unit_pair_list:
        unit_byte, unit_name = unit_pair
        if byte >= unit_byte:
            return unit_byte, unit_name

    return 1, "B"


def bytes_to_humanreadable(byte):
    byte = int(byte)
    if byte < 0:
        raise ValueError("argument must be greatar than 0")

    divisor, unit = _get_unit(byte)

    if (byte % divisor) == 0 and byte >= 1:
        value = str(int(byte / divisor))
    else:
        value = str(safe_division(byte, divisor))

    return value + " " + unit


def command_to_filename(command, suffix=""):
    sep_char = "/\\"

    command = command.strip()
    filename = command.replace(" ", "_")
    filename = filename.replace("-", "")
    filename = filename.strip(sep_char).lstrip(sep_char)
    filename = re.sub("[%s]" % re.escape("/\\"), "-", filename)
    filename = pathvalidate.sanitize_filename(filename)
    if dataproperty.is_not_empty_string(suffix):
        filename += "_" + suffix

    return filename


def compare_version(lhs_version, rhs_version):
    """
    <Major>.<Minor>.<Revision> 形式のバージョン文字列を比較する。

    :return:
        0<:	LHSがRHSより小さい
        0:	LHS == RHS
        0>:	LHSがRHSより大きい
    :rtype: int
    """

    lhs_major, lhs_minor, lhs_revision = [
        int(v) for v in lhs_version.split(".")]
    rhs_major, rhs_minor, rhs_revision = [
        int(v) for v in rhs_version.split(".")]

    if lhs_major < rhs_major:
        return -1
    elif lhs_major > rhs_major:
        return 1

    if lhs_minor < rhs_minor:
        return -1
    elif lhs_minor > rhs_minor:
        return 1

    if lhs_revision < rhs_revision:
        return -1
    elif lhs_revision > rhs_revision:
        return 1

    return 0


def get_execution_command():
    def get_arg_text():
        arg_list = []
        for arg in sys.argv[1:]:
            if dataproperty.is_integer(arg):
                arg_list.append(arg)
                continue

            if re.search("[\s]+", arg) is not None:
                arg = "'%s'" % (arg)
            arg_list.append(arg)

        return " ".join(arg_list)

    return os.path.basename(sys.argv[0]) + " " + get_arg_text()


def sleep_wrapper(sleep_second, dry_run=False):
    import time

    if sleep_second == float("inf"):
        # Process to maintain consistency between OS
        #   linux: raise IOError
        #   windows: raise OverflowError
        raise OverflowError("sleep length is too large")

    if dataproperty.is_nan(sleep_second):
        # Process to maintain consistency between OS
        #   linux: raise IOError
        #   windows: not raise exception
        raise IOError("Invalid argument")

    sleep_second = float(sleep_second)
    if sleep_second <= 0:
        return 0

    if dry_run:
        return 0

    time.sleep(sleep_second)

    return sleep_second


def get_var_name(var, symboltable):
    for name, v in six.iteritems(symboltable):
        if id(v) == id(var):
            return name


def dump_dict(dict_input, indent=4):
    """
    辞書型変数を文字列に変換して返す
    """

    dict_work = dict(dict_input)
    """
    for key, value in six.iteritems(dict_input):
        if any([f(value) for f in (is_float, isDict, is_list_or_tuple)]):
            dict_work[key] = value
            continue

        try:
            dict_work[key] = str(value)
        except:
            dict_work[key] = str(type(value))

        dict_work[key] = _convert_dump_dict(value)
    """

    try:
        import json
        return json.dumps(dict_work, sort_keys=True, indent=indent)
    except ImportError:
        pass

    try:
        import simplejson as json
        return json.dumps(dict_work, sort_keys=True, indent=indent)
    except ImportError:
        pass

    try:
        import pprint
        return pprint.pformat(dict_work, indent=indent)
    except ImportError:
        pass

    return str(dict_work)
