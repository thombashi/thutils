# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

import re
import sys
import datetime

import dataproperty
from thutils.logger import logger


class RegularExpression:

    class ISO:
        YEAR = "[1-2][\d]{3}"
        DATE = YEAR + "-[0-1][\d]-[0-3][\d]"
        TIME = "[0-2][0-9]:[0-5][0-9]:[0-5][0-9]"
        DATETIME = " ".join([DATE, TIME])
        TIMEZONE = "[+-][\d]{4}"
        DATETIME_WITH_TZ = " ".join([DATETIME, TIMEZONE])


class Format:

    class ISO8601:

        class Basic:
            DATE = "%Y%m%d"
            TIME = "%H%M%S"
            DATETIME = "T".join([DATE, TIME])

        class Extended:
            DATE = "%Y-%m-%d"
            TIME = "%H:%M:%S"
            DATETIME = "T".join([DATE, TIME]) + "%z"

    class ISO:
        DATE = "%Y-%m-%d"
        TIME = "%H:%M:%S"
        DATETIME = " ".join([DATE, TIME])

    ISO_DATETIME_LIST = [
        ISO.DATETIME,
        ISO8601.Basic.DATETIME,
        ISO8601.Extended.DATETIME,
    ]

    DATETIME_LIST = ISO_DATETIME_LIST + [
        " ".join(["%Y/%m/%d", ISO.TIME]),
    ]

    JST_DATE = "%Y/%m/%d"


def is_datetime(value):
    return value is not None and isinstance(value, datetime.datetime)


def is_valid_time_format(datetime_string, time_format):
    try:
        datetime.datetime.strptime(datetime_string, time_format)
    except (TypeError, ValueError):
        _, e, _ = sys.exc_info()  # for python 2.5 compatibility
        logger.debug(e)
        return False

    return True


def toDateTime(datetime_string, time_format, timezone=""):
    try:
        datetime_string = str(datetime_string)
    except UnicodeEncodeError:
        return None

    try:
        return_datetime = datetime.datetime.strptime(
            datetime_string.strip(), time_format)
    except ValueError:
        _, e, _ = sys.exc_info()  # for python 2.5 compatibility
        logger.debug(e)
        return None

    match = re.search(RegularExpression.ISO.TIMEZONE, timezone)
    if match is not None:
        tz = match.group()
        op = tz[0]
        hours = int(tz[1:3])
        minutes = int(tz[3:5])
        td = datetime.timedelta(hours=hours, minutes=minutes)
        if op == "+":
            return_datetime += td
        else:
            return_datetime -= td

    return return_datetime


def toDateTimeEx(datetime_string, time_format_list):
    time_format = findValidTimeFormat(
        datetime_string, time_format_list)

    if time_format is None:
        raise ValueError(
            "there is no matching time format: valid-format=%s, input=%s" % (
                "|".join(time_format_list), datetime_string))

    return toDateTime(datetime_string, time_format)


def findValidTimeFormat(datetime_string, time_format_list):
    for time_format in time_format_list:
        if is_valid_time_format(datetime_string, time_format):
            return time_format

    return None


def getTimeUnitSecondsCoefficient(unit):
    unit = unit.lower()

    unit_table = {
        "s": 1,
        "m": 60,
        "h": 60 ** 2,
        "d": 60 ** 2 * 24,
        "w": 60 ** 2 * 24 * 7,
    }

    coef_second = unit_table.get(unit)

    if coef_second is None:
        raise ValueError("invalid unit: " + str(unit))

    return coef_second


def getTimeDeltaSecond(start_datetime, end_datetime):
    deltatime = (end_datetime - start_datetime)
    return (
        deltatime.days * getTimeUnitSecondsCoefficient("d") +
        float(deltatime.seconds) +
        float(deltatime.microseconds / (1000.0 ** 2)))


def convertHumanReadableToSecond(readable_time):
    if dataproperty.is_empty_string(readable_time):
        raise ValueError("empty input")

    size = float(readable_time[:-1])
    unit = readable_time[-1]

    if size < 0:
        raise ValueError("minus size")

    return size * getTimeUnitSecondsCoefficient(unit)
