# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

import re
import sys
import datetime

from thutils.logger import logger
import thutils.common as common


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
            DATETIME = "T".join([DATE, TIME])

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


class DateTimeRange(common.BaseObject):

    @property
    def start_datetime(self):
        return self.__start_datetime

    @property
    def end_datetime(self):
        return self.__end_datetime

    def __init__(
            self, start_datetime, end_datetime,
            time_format=Format.ISO.DATETIME):

        super(DateTimeRange, self).__init__()
        self.__start_datetime = start_datetime
        self.__end_datetime = end_datetime
        self.time_format = time_format

    def equals(self, rhs):
        return all([
            self.start_datetime == rhs.start_datetime,
            self.end_datetime == rhs.end_datetime,
        ])

    def verifyTimeRange(self):
        """
        raise:
                TypeError
                ValueError
        """

        if self.start_datetime > self.end_datetime:
            message = "time inversion found: %s > %s" % (
                str(self.start_datetime), str(self.end_datetime))
            raise ValueError(message)

    def isValidTimeRange(self):
        try:
            self.verifyTimeRange()
        except (TypeError, ValueError):
            return False

        return True

    def isWithin(self, input_datetime):
        self.verifyTimeRange()

        return self.start_datetime <= input_datetime <= self.end_datetime

    def getStartTimeText(self):
        return self.__to_datetime_text(self.start_datetime)

    def getEndTimeText(self):
        return self.__to_datetime_text(self.end_datetime)

    def getOptionString(self):
        self.__verify_time_format()

        options_list = []

        if is_datetime(self.start_datetime):
            options_list.extend(
                ["-s", "'%s'" % (self.getStartTimeText())])

        if is_datetime(self.end_datetime):
            options_list.extend(
                ["-e", "'%s'" % (self.getEndTimeText())])

        return " ".join(options_list)

    def getTimeDelta(self):
        """
        Return value:
                datetime.timedelta
        """

        return self.end_datetime - self.start_datetime

    def getDeltaSecond(self):
        dt = self.getTimeDelta()

        return (
            dt.days * getTimeUnitSecondsCoefficient("d") +
            float(dt.seconds) + float(dt.microseconds / (1000.0 ** 2)))

    def to_string(self, joint=" - ", time_format=None):
        if not self.isValidTimeRange():
            return ""

        old_time_format = None
        if common.is_not_empty_string(time_format):
            old_time_format = self.time_format
            self.time_format = time_format

        text_list = [
            self.getStartTimeText(),
            self.getEndTimeText(),
        ]
        return_value = (
            joint.join(text_list) +
            " (%s)" % (self.end_datetime - self.start_datetime)
        )

        if common.is_not_empty_string(old_time_format):
            self.time_format = old_time_format

        return return_value

    def squeezeTimeRange(self, datetime_range):
        """
        time inversionを発生させない範疇で時間範囲を狭める。
        """

        start = datetime_range.start_datetime
        if is_datetime(start):
            if not is_datetime(self.start_datetime):
                self.__start_datetime = start
            elif is_datetime(self.end_datetime) and self.isWithin(start):
                self.__start_datetime = max(self.start_datetime, start)

        end = datetime_range.end_datetime
        if is_datetime(end):
            if not is_datetime(self.end_datetime):
                self.__end_datetime = end
            elif is_datetime(self.start_datetime) and self.isWithin(end):
                self.__end_datetime = min(self.end_datetime, end)

    def widenTimeRange(self, datetime_range):
        """
        時間範囲を広げる。
        """

        start = datetime_range.start_datetime
        if is_datetime(start):
            if not is_datetime(self.start_datetime):
                self.__start_datetime = start
            else:
                self.__start_datetime = min(self.start_datetime, start)

        end = datetime_range.end_datetime
        if is_datetime(end):
            if not is_datetime(self.end_datetime):
                self.__end_datetime = end
            else:
                self.__end_datetime = max(self.end_datetime, end)

    def discard(self, discard_percent):
        """
        時間範囲の discard_percent / 2 [%] の時間分、開始・終了時刻をずらす。
        """

        self.verifyTimeRange()

        if discard_percent == 0:
            return True

        if discard_percent < 0:
            raise ValueError(
                "discard_percent must be greater than zero: " +
                str(discard_percent))

        discard_time = self.getTimeDelta() // int(100) * \
            int(discard_percent / 2.0)

        self.__start_datetime += discard_time
        self.__end_datetime -= discard_time

        return True

    def __verify_time_format(self):
        if re.search(re.escape("%"), self.time_format) is None:
            raise ValueError("invalid time format: " + self.time_format)

    def __to_datetime_text(self, dt):
        if not is_datetime(dt):
            return ""

        self.__verify_time_format()

        return dt.strftime(self.time_format)


class TimeMeasure(object):
    import logging

    # Message Format ---
    __MF_START = "<start %s> %s"
    __MF_COMPLETE = "<complete> %s: execution-time=%s"

    @property
    def message(self):
        return self.__message

    def __init__(self, message, log_level=logging.INFO):
        import os
        import socket

        self.__measurent_emtimerange = None
        self.__message = message
        self.__log_level = log_level

        self.start()

        # output message ---
        hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            ip_address = "na"

        header = "%s(%s) %s$ " % (hostname, ip_address, os.getcwd())
        write_message = self.__MF_START % (
            self.__start_datetime.strftime(Format.ISO.DATETIME),
            header + self.message)
        logger.write(write_message, self.__log_level)

    def start(self):
        self.__start_datetime = datetime.datetime.now()

    def stop(self):
        end_datetime = datetime.datetime.now()
        self.__measurent_emtimerange = DateTimeRange(
            self.__start_datetime, end_datetime)

        return self.__measurent_emtimerange

    def __del__(self):
        datetimerange = self.stop()
        complete_msg = self.__MF_COMPLETE % (
            self.message,
            datetimerange.to_string())
        logger.write(complete_msg, self.__log_level)


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
    if common.is_empty_string(readable_time):
        raise ValueError("empty input")

    size = float(readable_time[:-1])
    unit = readable_time[-1]

    if size < 0:
        raise ValueError("minus size")

    return size * getTimeUnitSecondsCoefficient(unit)
