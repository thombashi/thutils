# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

import pytest
from thutils.gtime import *


def setup_module(module):
    import locale

    locale.setlocale(locale.LC_ALL, 'C')


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
