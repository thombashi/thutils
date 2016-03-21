# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''


import dataproperty


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


def convertHumanReadableToSecond(readable_time):
    if dataproperty.is_empty_string(readable_time):
        raise ValueError("empty input")

    size = float(readable_time[:-1])
    unit = readable_time[-1]

    if size < 0:
        raise ValueError("minus size")

    return size * getTimeUnitSecondsCoefficient(unit)
