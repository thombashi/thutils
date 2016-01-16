# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

from __future__ import with_statement
import os.path
import re
import sys

import six

from thutils.logger import logger


# Key ---
KEY_AVERAGE = "key-avg"
KEY_TOTAL = "key-total"
KEY_ALL = "key-all"

# Attribute Name ---
AN_GeneralKey = "key"
AN_GeneralValue = "value"
AN_GeneralGroupID = "group_id"
AN_SamplingStartTime = "Sampling Start Time"
AN_SamplingEndTime = "Sampling End Time"
KEY_VALUE_HEADER = [AN_GeneralKey, AN_GeneralValue]


class Field:
    GENERAL_KEY = "key"
    GENERAL_VALUE = "value"
    DATETIME = "datetime"
    SAMPLING_START_TIME = "Sampling Start Time"
    SAMPLING_END_TIME = "Sampling END Time"


# Regular Expression ---
RE_SPACE = re.compile("[\s]+")


class NotInstallError(Exception):
    pass


class BaseObject(object):

    def __init__(self):
        pass

    def toString(self):
        return "%s: %s" % (
            self.__class__.__name__, dump_dict(self.__dict__))

    def debug(self, message=""):
        logger.debug("%s: %s %s" % (
            self.__class__.__name__, message, dump_dict(self.__dict__)))


class MinMaxObject(BaseObject):

    @property
    def min_value(self):
        return self.__min_value

    @property
    def max_value(self):
        return self.__max_value

    def __init__(self):
        self.__min_value = None
        self.__max_value = None

    def diff(self):
        return self.max_value - self.min_value

    def average(self):
        return (self.max_value + self.min_value) * 0.5

    def update(self, value):
        if self.__min_value is None:
            self.__min_value = value
        else:
            self.__min_value = min(self.__min_value, value)

        if self.__max_value is None:
            self.__max_value = value
        else:
            self.__max_value = max(self.__max_value, value)


def isInteger(value):
    if isinstance(value, six.integer_types):
        return not isinstance(value, bool)

    try:
        int(value)
    except:
        return False

    text = str(value).strip()
    if re.search("[.]|e-", text) is not None:
        return False

    return True


def isHex(value):
    try:
        int(value, 16)
    except (TypeError, ValueError):
        return False

    return True


def isFloat(value):
    if any([isinstance(value, float), value == float("inf")]):
        return True

    if isinstance(value, bool):
        return False

    try:
        work = float(value)
        if work == float("inf"):
            return False
    except:
        return False

    return True


def isNaN(value):
    return value != value


def isList(value):
    return isinstance(value, list)


def isTuple(value):
    return isinstance(value, tuple)


def isListOrTuple(value):
    return any([isList(value), isTuple(value)])


def isNotEmptyString(value):
    """
    空白文字(\0, \t, \n)を除いた文字数が0より大きければTrueを返す
    """

    try:
        return len(value.strip()) > 0
    except AttributeError:
        return False


def isEmptyString(value):
    try:
        return len(value.strip()) == 0
    except AttributeError:
        return True


def isEmptyList(value):
    return value is None or (isList(value) and len(value) == 0)


def isEmptyTuple(value):
    return value is None or (isTuple(value) and len(value) == 0)


def isEmptyListOrTuple(value):
    return value is None or (isListOrTuple(value) and len(value) == 0)


def isNotEmptyListOrTuple(value):
    return isListOrTuple(value) and len(value) > 0


def safe_division(dividend, divisor):
    """
    return value:
            nan: invalid arguments
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


def get_list_item(input_list, index):
    if isEmptyList(input_list):
        logger.debug("null input_list")
        return None

    list_size = len(input_list)
    if not (0 <= index < list_size):
        message = "out of index: list=%s, size=%d, index=%s" % (
            input_list, list_size, str(index))
        #raise IndexError(message)
        logger.debug(message)
        return None

    try:
        return input_list[index]
    except TypeError:
        return None


def get_integer_digit(value):
    import math

    abs_value = abs(float(value))

    if abs_value == 0:
        return 1

    return max(1, int(math.log10(abs_value) + 1.0))


def _get_decimal_places(value, significant_digit):
    float_digit_len = 0
    if isInteger(value):
        abs_value = abs(int(value))
    else:
        abs_value = abs(float(value))
        text_value = str(abs_value)
        float_text = 0
        if text_value.find(".") != -1:
            float_text = text_value.split(".")[1]
            float_digit_len = len(float_text)
        elif text_value.find("e-") != -1:
            float_text = text_value.split("e-")[1]
            float_digit_len = int(float_text) - 1

    abs_digit = 0
    significant_digit = int(significant_digit)
    if significant_digit <= 1:
        if abs_value < 0.01:
            abs_digit = 5
        elif abs_value < 0.1:
            abs_digit = 4
        else:
            abs_digit = 3
    elif significant_digit <= 2:
        abs_digit = 2
    elif significant_digit <= 3:
        abs_digit = 1

    return min(abs_digit, float_digit_len)


def get_number_of_digit(value):
    try:
        integer_digits = get_integer_digit(value)
    except (ValueError, TypeError):
        integer_digits = float("nan")

    try:
        decimal_places = _get_decimal_places(value, integer_digits)
    except (ValueError, TypeError):
        decimal_places = float("nan")

    return (integer_digits, decimal_places)


def getTextLen(text):
    try:
        return len(str(text))
    except UnicodeEncodeError:
        return len(text)
    except:
        return 0


def removeItemFromList(item_list, item):
    is_remove = False
    if item in item_list:
        item_list.remove(item)
        is_remove = True

    return is_remove


def removeListFromList(input_list, remove_list):
    for remove_item in remove_list:
        removeItemFromList(input_list, remove_item)


def convertValue(value):
    if isInteger(value):
        value = int(value)
    elif isFloat(value):
        value = float(value)

    return value


def diffItemList(item_list, remove_list):
    # return list(set(item_list).difference(set(remove_list)))
    work_list = list(item_list)
    for remove_item in remove_list:
        removeItemFromList(work_list, remove_item)

    return work_list


"""
def makeRandomString(self, min_len, max_len):
    import random
    import string

    name_len = random.randint(min_len, max_len)
    name = "".join([
        random.choice(string.ascii_letters + string.digits) for _ in range(name_len)
    ])

    return "%s.%s" % (name)
#"""


def _unit_to_byte(unit):
    kilo = int(1024)

    re_exp_pair_list = [
        [re.compile("^b$", re.IGNORECASE), 0],
        [re.compile("^k$", re.IGNORECASE), 1],
        [re.compile("^m$", re.IGNORECASE), 2],
        [re.compile("^g$", re.IGNORECASE), 3],
        [re.compile("^t$", re.IGNORECASE), 4],
        [re.compile("^p$", re.IGNORECASE), 5],
    ]

    for re_exp_pair in re_exp_pair_list:
        re_pattern, exp = re_exp_pair

        if re_pattern.search(unit):
            return kilo ** exp

    raise ValueError("unknown unit: %s" % (unit))


def humanreadable_to_byte(readable_size):
    """
    :argument:
        readable size:
            human readable size (bytes).
            e.g. 256 M
    """

    size = readable_size[:-1]
    unit = readable_size[-1]
    if not isFloat(size):
        raise ValueError(
            "invalid value: size='%s', input=%s" % (size, readable_size))
    if not unit.isalpha():
        raise ValueError(
            "invalid unit: unit=%s, input=%s" % (unit, readable_size))
    size = float(size)
    unit = unit.lower()

    if size < 0:
        raise ValueError("minus size")

    coefficient = _unit_to_byte(unit)

    return size * coefficient


def humanreadable_to_kb(readable_size):
    return humanreadable_to_byte(readable_size) / 1024


def bytes_to_humanreadable(byte):
    byte = int(byte)
    if byte < 0:
        raise ValueError("argument must be greatar than 0")

    kilo = 1024

    if byte >= kilo ** 4:
        divisor = kilo ** 4
        unit = "TB"
    elif byte >= kilo ** 3:
        divisor = kilo ** 3
        unit = "GB"
    elif byte >= kilo ** 2:
        divisor = kilo ** 2
        unit = "MB"
    elif byte >= kilo ** 1:
        divisor = kilo ** 1
        unit = "KB"
    else:
        divisor = 1
        unit = "B"

    if divisor == 1:
        return str(byte) + " " + unit

    if (byte % divisor) == 0 and byte >= 1:
        value = str(int(byte / divisor))
    else:
        value = str(safe_division(byte, divisor))

    return value + " " + unit


def strtobool_wrapper(value):
    """
    try:
        import distutils.util
        return bool(distutils.util.strtobool(value))
    except ImportError:
    """

    re_true = re.compile("^true$", re.IGNORECASE)
    re_false = re.compile("^false$", re.IGNORECASE)
    if re_true.match(value):
        return True
    if re_false.match(value):
        return False

    raise ValueError("can not convert '%s' to bool" % (value))


# no unit test ------


def splitLineList(line_list, separator=""):
    line_idx = 0
    for line in line_list:
        if line.strip() == separator:
            line_idx += 1
            continue

        break

    return splitLineListByRe(
        line_list[line_idx:],
        re.compile("^%s$" % (separator)),
        is_include_matched_line=False)


def splitLineListByRe(
        line_list, re_separator, is_include_matched_line=False, is_strip=True):
    block_list = []
    block = []

    for line in line_list:
        if is_strip:
            line = line.strip()

        if re_separator.search(line):
            block_list.append(block)
            block = []
            if is_include_matched_line:
                block.append(line)
            continue

        block.append(line)

    if len(block) > 0:
        block_list.append(block)

    logger.debug(
        "splitLineListByRe: block-count=%s" % (len(block_list)))

    return block_list


def splitLineListByReEx(
        line_list, re_separator, is_include_matched_line=False, is_strip=True):
    block_list = []
    block = []

    for line in line_list:
        if is_strip:
            line = line.strip()

        if re_separator.search(line):
            if is_include_matched_line:
                block.append(line)
            block_list.append(block)
            block = []
            continue

        block.append(line)

    if len(block) > 0:
        block_list.append(block)

    logger.debug(
        "splitLineListByRe: block-count=%s" % (len(block_list)))

    return block_list


def is_install_command(command):
    import subprocess
    import platform

    if platform.system() != "Linux":
        return False

    search_command = "type " + command.split()[0]
    proc = subprocess.Popen(
        search_command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    isCommandFound = proc.wait() == 0
    if not isCommandFound:
        logger.debug("'%s' command not found" % (command))

    return isCommandFound


def verify_install_command(command_list):
    not_installed_command_list = []

    for command in command_list:
        if not is_install_command(command):
            not_installed_command_list.append(command)

    if len(not_installed_command_list) > 0:
        message = "command not found: %s" % (
            ", ".join(not_installed_command_list))
        raise NotInstallError(message)

    logger.debug("required commands are installed: " + ", ".join(command_list))


def command_to_filename(command, suffix=""):
    import thutils.gfile as gfile

    command = command.strip()
    filename = command.replace(" ", "_")
    filename = filename.replace("-", "")
    filename = filename.strip(os.path.sep)
    filename = filename.replace(os.path.sep, "-")
    filename = gfile.sanitizeFileName(filename)
    if isNotEmptyString(suffix):
        filename += "_" + suffix

    return filename


def compare_version(lhs_version, rhs_version):
    """
    <Major>.<Minor>.<Revision> 形式のバージョン文字列を比較する。

    Return value:
            0<:	LHSがRHSより小さい
            0:	LHS == RHS
            0>:	LHSがRHSより大きい
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
            if isInteger(arg):
                arg_list.append(arg)
                continue

            if RE_SPACE.search(arg):
                arg = "'%s'" % (arg)
            arg_list.append(arg)

        return " ".join(arg_list)

    return os.path.basename(sys.argv[0]) + " " + get_arg_text()


def sleep_wrapper(sleep_second, dry_run=False):
    import time

    sleep_second = float(sleep_second)
    if sleep_second <= 0:
        logger.debug("skip sleep")
        return 0

    if dry_run:
        logger.debug("dry-run: skip sleep")
        return 0

    logger.debug("sleep %f seconds" % (sleep_second))
    time.sleep(sleep_second)

    return sleep_second


def get_var_name(var, symboltable):
    for name, v in symboltable.iteritems():
        if id(v) == id(var):
            return name


# dict ---

def _convert_dump_dict(value):
    if isInteger(value):
        return int(value)

    if isFloat(value):
        return float(value)

    try:
        return dict(value)
    except:
        pass

    try:
        return list(value)
    except:
        pass

    try:
        return str(value)
    except:
        pass

    try:
        return str(type(value))
    except:
        pass


def dump_dict(dict_input, indent=4):
    """
    辞書型変数を文字列に変換して返す
    """

    dict_work = dict(dict_input)
    """
    for key, value in six.iteritems(dict_input):
        if any([f(value) for f in (isFloat, isDict, isListOrTuple)]):
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
    except Exception:
        _, e, _ = sys.exc_info()  # for python 2.5 compatibility
        logger.exception(e)

    try:
        import simplejson as json
        return json.dumps(dict_work, sort_keys=True, indent=indent)
    except ImportError:
        pass
    except Exception:
        _, e, _ = sys.exc_info()  # for python 2.5 compatibility
        logger.exception(e)

    logger.error("failed to import json library")

    try:
        import pprint
        return pprint.pformat(dict_work, indent=indent)
    except ImportError:
        pass

    return str(dict_work)


def debug_dict(dict_input, symbol_table, convert_func=dump_dict):
    logger.debug("%s keys=%d %s" % (
        get_var_name(dict_input, symbol_table),
        len(dict_input), convert_func(dict_input)))


def dict_to_matrix(input_dict, key_list=()):
    if isEmptyListOrTuple(key_list):
        key_list = six.iterkeys(input_dict)

    matrix = []
    for key in key_list:
        value = input_dict.get(key)
        if isListOrTuple(value):
            value = ", ".join([str(x) for x in value])
        matrix.append([key, value])

    return matrix
