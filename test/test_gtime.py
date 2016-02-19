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


class Test_TimeMeasure:

    def test_smoke(self):
        TimeMeasure("test")


class Test_is_datetime:

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


class Test_is_valid_time_format:

    @pytest.mark.parametrize(["value", "time_format", "expected"], [
        [START_DATETIME_TEXT, Format.ISO.DATETIME, True],
        [START_DATETIME_TEXT, Format.ISO8601.Basic.DATETIME, False],
        ["May 13, 2014", "%b %d, %Y", True],
    ])
    def test_normal(self, value, time_format, expected):
        import locale

        locale.setlocale(locale.LC_TIME, "C")
        assert is_valid_time_format(value, time_format) == expected

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
        assert is_valid_time_format(value, time_format) == expected


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
