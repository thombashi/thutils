# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required:
    https://pypi.python.org/pypi/pytest
'''

import datetime

import pytest

from thutils.gtime import *


START_DATETIME_TEXT = "2015-03-22 10:00:00"
ISO_DATETIME_TEXT = "2015-03-22 10:00:00"

TEST_START_DATETIME = toDateTime(
    START_DATETIME_TEXT, Format.ISO.DATETIME)
TEST_END_DATETIME = toDateTime(
    "2015-03-22 10:10:00", Format.ISO.DATETIME)


def setup_module(module):
    import locale

    locale.setlocale(locale.LC_ALL, 'C')


class Test_DateTimeRange:

    @pytest.fixture
    def datetime_range(self):
        datetime_range = DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME)
        datetime_range.time_format = Format.ISO.DATETIME
        return datetime_range

    def test_verifyTimeRange(self, datetime_range):
        datetime_range.verifyTimeRange()

    def test_verifyTimeFormat(self, datetime_range):
        datetime_range.verifyTimeFormat()

    def test_isValidTimeRange(self, datetime_range):
        assert datetime_range.isValidTimeRange()

    @pytest.mark.parametrize(["inpute_datetime", "expected"], [
        [TEST_START_DATETIME, True],
        [TEST_END_DATETIME, True],
        [toDateTime("2015-03-22 09:59:59", Format.ISO.DATETIME), False],
        [toDateTime("2015-03-22 10:10:01", Format.ISO.DATETIME), False],
    ])
    def test_isWithin_normal(self, datetime_range, inpute_datetime, expected):
        assert datetime_range.isWithin(inpute_datetime) == expected

    @pytest.mark.parametrize(["inpute_datetime", "expected"], [
        [None, TypeError],
        [False, TypeError],
        [20140513221937, TypeError],
        [START_DATETIME_TEXT, TypeError],
    ])
    def test_isWithin_abnormal(
            self, datetime_range, inpute_datetime, expected):
        with pytest.raises(expected):
            datetime_range.isWithin(inpute_datetime)

    @pytest.mark.parametrize(["expected"], [
        [START_DATETIME_TEXT],
    ])
    def test_getStartTimeText(self, datetime_range, expected):
        assert datetime_range.getStartTimeText() == expected

    @pytest.mark.parametrize(["expected"], [
        ["2015-03-22 10:10:00"],
    ])
    def test_getEndTimeText(self, datetime_range, expected):
        assert datetime_range.getEndTimeText() == expected

    @pytest.mark.parametrize(["expected"], [
        ["-s '2015-03-22 10:00:00' -e '2015-03-22 10:10:00'"],
    ])
    def test_getOptionString(self, datetime_range, expected):
        assert datetime_range.getOptionString() == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [1, TypeError],
        [True, TypeError],
    ])
    def test_getOptionString_exception(self, datetime_range, value, expected):
        with pytest.raises(expected):
            datetime_range.getOptionString(value)

    def test_getTimeDelta(self, datetime_range):
        assert datetime_range.getTimeDelta() == datetime.timedelta(
            seconds=10 * 60)

    def test_getDeltaSecond(self, datetime_range):
        assert datetime_range.getDeltaSecond() == 600

    @pytest.mark.parametrize(["joint", "time_format", "expected"], [
        [
            " - ", None,
            "2015-03-22 10:00:00 - 2015-03-22 10:10:00 (0:10:00)",
        ],
        [
            " to ", None,
            "2015-03-22 10:00:00 to 2015-03-22 10:10:00 (0:10:00)",
        ],
        [
            "-", Format.ISO8601.Basic.DATETIME,
            "20150322T100000-20150322T101000 (0:10:00)",
        ],
    ])
    def test_toString(self, datetime_range, joint, time_format, expected):
        assert datetime_range.toString(joint, time_format) == expected

    @pytest.mark.parametrize(["joint", "time_format", "expected"], [
        [
            None, None, AttributeError,
        ],
    ])
    def test_toString_abnormal(
            self, datetime_range, joint, time_format, expected):
        with pytest.raises(expected):
            datetime_range.toString(joint, time_format)

    def test_squeezeTimeRange(self, datetime_range):

        value = DateTimeRange(
            toDateTime("2015-03-22 10:00:10", Format.ISO.DATETIME),
            toDateTime("2015-03-22 10:09:50", Format.ISO.DATETIME))
        datetime_range.squeezeTimeRange(value)
        assert datetime_range.equals(value)

    def test_widenTimeRange(self, datetime_range):
        value = DateTimeRange(
            toDateTime("2015-03-22 09:59:00", Format.ISO.DATETIME),
            toDateTime("2015-03-22 10:11:00", Format.ISO.DATETIME))
        datetime_range.widenTimeRange(value)
        assert datetime_range.equals(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [0, DateTimeRange(TEST_START_DATETIME, TEST_END_DATETIME)],
        [
            10,
            DateTimeRange(
                toDateTime("2015-03-22 10:00:30", Format.ISO.DATETIME),
                toDateTime("2015-03-22 10:09:30", Format.ISO.DATETIME))
        ],
    ])
    def test_discard(self, datetime_range, value, expected):
        assert datetime_range.discard(value)
        assert datetime_range.equals(expected)


class Test_DateTimeRange_abnormal:

    @pytest.fixture
    def datetime_range(self):
        value = DateTimeRange(None, TEST_END_DATETIME)
        value.time_format = None
        return value

    def test_verifyTimeRange(self, datetime_range):
        with pytest.raises(TypeError):
            datetime_range.verifyTimeRange()

    def test_verifyTimeFormat(self, datetime_range):
        with pytest.raises(TypeError):
            datetime_range.verifyTimeFormat()

    def test_isValidTimeRange(self, datetime_range):
        assert not datetime_range.isValidTimeRange()

    @pytest.mark.parametrize(['inpute_datetime'], [
        [TEST_START_DATETIME],
    ])
    def test_isWithin_normal(self, datetime_range, inpute_datetime):
        with pytest.raises(TypeError):
            datetime_range.isWithin(inpute_datetime)

    def test_getStartTimeText(self, datetime_range):
        assert datetime_range.getStartTimeText() == ""

    def test_getEndTimeText(self, datetime_range):
        with pytest.raises(TypeError):
            datetime_range.getEndTimeText()

    def test_getOptionString(self, datetime_range):
        with pytest.raises(TypeError):
            datetime_range.getOptionString()

    def test_getTimeDelta(self, datetime_range):
        with pytest.raises(TypeError):
            datetime_range.getTimeDelta()

    @pytest.mark.parametrize(["joint", "time_format", "expected"], [
        [None, None, ""],
        [" - ", "", ""],
    ])
    def test_toString(self, datetime_range, joint, time_format, expected):
        assert datetime_range.toString(joint, time_format) == expected

    def test_squeezeTimeRange(self, datetime_range):
        value = DateTimeRange(
            toDateTime("2015-03-22 10:00:10", Format.ISO.DATETIME),
            toDateTime("2015-03-22 10:09:50", Format.ISO.DATETIME))
        datetime_range.squeezeTimeRange(value)
        assert datetime_range.equals(value)

    def test_widenTimeRange(self, datetime_range):
        value = DateTimeRange(
            toDateTime("2015-03-22 09:59:00", Format.ISO.DATETIME),
            toDateTime("2015-03-22 10:11:00", Format.ISO.DATETIME))
        datetime_range.widenTimeRange(value)
        assert datetime_range.equals(value)

    @pytest.mark.parametrize(['discard_percent'], [
        [0],
    ])
    def test_discard(self, datetime_range, discard_percent):
        with pytest.raises(TypeError):
            assert datetime_range.discard(discard_percent)


class Test_isDatetime:

    @pytest.mark.parametrize(["value", "expected"], [
        [TEST_START_DATETIME, True],

        [None, False],
        ["", False],
        ["テスト", False],
        [[], False],
        [1, False],
        [True, False],
    ])
    def test_normal(self, value, expected):
        assert is_datetime(value) == expected


class Test_isValidTimeFormat:

    @pytest.mark.parametrize(["value", "time_format", "expected"], [
        [START_DATETIME_TEXT, Format.ISO.DATETIME, True],
        [START_DATETIME_TEXT, Format.ISO8601.Basic.DATETIME, False],
        ["May 13, 2014", "%b %d, %Y", True],
    ])
    def test_normal(self, value, time_format, expected):
        import locale

        locale.setlocale(locale.LC_TIME, "C")
        assert isValidTimeFormat(value, time_format) == expected

    @pytest.mark.parametrize(["value", "time_format", "expected"], [
        [None, Format.ISO.DATETIME, False],
        ["", Format.ISO.DATETIME, False],
        ["テスト", Format.ISO.DATETIME, False],
        [1, Format.ISO.DATETIME, False],
        [True, Format.ISO.DATETIME, False],
        [START_DATETIME_TEXT, "テスト", False],
        [START_DATETIME_TEXT, "", False],
        [START_DATETIME_TEXT, None, False],
        [START_DATETIME_TEXT, 1, False],
    ])
    def test_abnormal(self, value, time_format, expected):
        assert isValidTimeFormat(value, time_format) == expected


class Test_toDateTime:

    @pytest.mark.parametrize(["value", "time_format"], [
        [
            START_DATETIME_TEXT,
            Format.ISO.DATETIME,
        ],
        [
            ISO_DATETIME_TEXT,
            Format.ISO.DATETIME,
        ],
        [
            "May 13, 2014",
            "%b %d, %Y",
        ],
    ])
    def test_normal(self, value, time_format):
        import locale

        locale.setlocale(locale.LC_TIME, "C")
        expected = datetime.datetime.strptime(value, time_format)
        assert toDateTime(value, time_format) == expected

    @pytest.mark.parametrize(["value", "time_format", "expected"], [
        [START_DATETIME_TEXT, Format.JST_DATE, None],
        ["", Format.JST_DATE, None],
        ["テスト", Format.JST_DATE, None],
        [None, Format.JST_DATE, None],
        [1, Format.JST_DATE, None],
        [START_DATETIME_TEXT, "テスト", None],
        [START_DATETIME_TEXT, "", None],
    ])
    def test_abnormal(self, value, time_format, expected):
        assert toDateTime(value, time_format) == expected

    @pytest.mark.parametrize(["value", "time_format", "expected"], [
        [START_DATETIME_TEXT, None, TypeError],
        [START_DATETIME_TEXT, 1, TypeError],
    ])
    def test_exception(self, value, time_format, expected):
        with pytest.raises(expected):
            toDateTime(value, time_format)


class Test_findValidTimeFormat:

    @pytest.mark.parametrize(["value", "time_format_list", "expected"], [
        [
            START_DATETIME_TEXT,
            Format.ISO_DATETIME_LIST,
            Format.ISO.DATETIME
        ],

        [None, Format.ISO_DATETIME_LIST, None],
        ["", Format.ISO_DATETIME_LIST, None],
        ["テスト", Format.ISO_DATETIME_LIST, None],
    ])
    def test_normal(self, value, time_format_list, expected):
        assert findValidTimeFormat(value, time_format_list) == expected

    @pytest.mark.parametrize(["value", "time_format_list", "expected"], [
        [START_DATETIME_TEXT, None, TypeError],
    ])
    def test_exception(self, value, time_format_list, expected):
        with pytest.raises(expected):
            findValidTimeFormat(value, time_format_list)


class Test_getTimeUnitSecondsCoefficient:

    @pytest.mark.parametrize(["value", "expected"], [
        ["s", 1], ["S", 1],
        ["m", 60], ["M", 60],
        ["h", 60 ** 2], ["H", 60 ** 2],
        ["d", 60 ** 2 * 24], ["D", 60 ** 2 * 24],
        ["w", 60 ** 2 * 24 * 7], ["W", 60 ** 2 * 24 * 7],
    ])
    def test_normal(self, value, expected):
        assert getTimeUnitSecondsCoefficient(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, AttributeError],
        [1, AttributeError],
        ["a", ValueError],
        ["1s", ValueError],
        ["sec", ValueError],
        ["テスト", ValueError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            getTimeUnitSecondsCoefficient(value)


class Test_getTimeDeltaSecond:

    @pytest.mark.parametrize(["start", "end", "expected"], [
        [TEST_START_DATETIME, TEST_END_DATETIME, 600],
        [TEST_START_DATETIME, TEST_START_DATETIME, 0],
        [TEST_END_DATETIME, TEST_START_DATETIME, -600],
    ])
    def test_normal(self, start, end, expected):
        assert getTimeDeltaSecond(start, end) == expected

    @pytest.mark.parametrize(["start", "end", "expected"], [
        [None, TEST_START_DATETIME, TypeError],
        [TEST_START_DATETIME, None, TypeError],
        [None, None, TypeError],
        [1, 1, AttributeError],
    ])
    def test_exception(self, start, end, expected):
        with pytest.raises(expected):
            getTimeDeltaSecond(start, end)


class Test_convertHumanReadableToSecond:

    @pytest.mark.parametrize(["value", "expected"], [
        ["2s", 2], ["2S", 2],
        ["2.5s", 2.5], ["2.5S", 2.5],
        ["2m", 2 * 60], ["2M", 2 * 60],
        ["2h", 2 * 60 ** 2], ["2H", 2 * 60 ** 2],
        ["2d", 2 * 60 ** 2 * 24], ["2D", 2 * 60 ** 2 * 24],
        ["2w", 2 * 60 ** 2 * 24 * 7], ["2W", 2 * 60 ** 2 * 24 * 7],
        ["123456789 w", 123456789 * 60 ** 2 * 24 * 7],
        ["123456789 W", 123456789 * 60 ** 2 * 24 * 7],
    ])
    def test_normal(self, value, expected):
        assert convertHumanReadableToSecond(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        [True, ValueError],
        [1, ValueError],
        ["1", ValueError],
        ["s", ValueError],
        ["-1s", ValueError],
        ["1sec", ValueError],
        ["テスト", ValueError],
    ])
    def test_abnormal(self, value, expected):
        with pytest.raises(expected):
            convertHumanReadableToSecond(value)
