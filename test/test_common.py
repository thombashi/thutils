# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

import platform

import dataproperty
import pytest

from thutils.common import *
from thutils.gfile import *


nan = float("nan")
inf = float("inf")


class Test_safe_division:

    @pytest.mark.parametrize(['dividend', "divisor", "expected"], [
        [4, 2, 2],
        [-4, -2, 2],
        [4, -2, -2],
        [-4, 2, -2],
        [2, 4, 0.5],
        [200000000000000, 400000000000000, 0.5],
        [0, 2, 0],
        ["1", 2, 0.5],
        [1, "2", 0.5],
        [True, True, 1.0],
    ])
    def test_normal(self, dividend, divisor, expected):
        assert safe_division(dividend, divisor) == expected

    @pytest.mark.parametrize(['dividend', "divisor"], [
        [2, 0],
        [None, 1],
        [1, None],
        [None, None],
        ["a", 2],
        [1, "a"],
        ["a", "a"],
        [nan, 2],
        [2, nan],
        [nan, nan],
        [nan, inf],
        [inf, nan],
        [inf, inf],
        [True, False],
    ])
    def test_abnormal_1(self, dividend, divisor):
        assert dataproperty.is_nan(safe_division(dividend, divisor))

    @pytest.mark.parametrize(['dividend', "divisor", "expected"], [
        [inf, 2, inf],
        [-inf, 2, -inf],
        [2, inf, 0],
        [2, -inf, 0],
    ])
    def test_abnormal_2(self, dividend, divisor, expected):
        assert safe_division(dividend, divisor) == expected


class Test_removeItemFromList:

    def test_normal_1(self):
        arg_list = [1, 2, 3]

        assert removeItemFromList(arg_list, 2)
        assert arg_list == [1, 3]

    def test_abnormal_1(self):
        arg_list = [1, 2, 3]

        assert not removeItemFromList(arg_list, 4)
        assert arg_list == [1, 2, 3]

    def test_abnormal_2(self):
        with pytest.raises(TypeError):
            assert not removeItemFromList(None, 4)


class Test_removeListFromList:

    def test_normal_1(self):
        arg_list = [1, 2, 3, 4]
        remove_list = [2, 3]

        removeListFromList(arg_list, remove_list)
        assert arg_list == [1, 4]

    def test_abnormal_1(self):
        arg_list = [1, 2, 3]
        remove_list = [4, 5]

        removeListFromList(arg_list, remove_list)
        assert arg_list == [1, 2, 3]


class Test_bytes_to_humanreadable:

    @pytest.mark.parametrize(["value", "expected"], [
        [2, "2 B"],
        [2 * 1024 ** 1, "2 KB"],
        [2 * 1024 ** 2, "2 MB"],
        [2 * 1024 ** 3, "2 GB"],
        [2 * 1024 ** 4, "2 TB"],
        [int(2.5 * 1024 ** 2), "2.5 MB"],
        [2.5 * 1024 ** 2, "2.5 MB"],
    ])
    def test_normal_1(self, value, expected):
        assert bytes_to_humanreadable(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [nan, ValueError],
        [inf, OverflowError],
        [-1, ValueError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            bytes_to_humanreadable(value)


class Test_command_to_filename:

    @pytest.mark.parametrize(["value", "suffix", "expected"], [
        ["/bin/ls", "", "bin-ls"],
        ["/bin/ls", None, "bin-ls"],
        ["/bin/ls -la", "test", "bin-ls_la_test"],
        ["cat /proc/cpuinfo", "", "cat_-proc-cpuinfo"],
        ["", "", ""],
    ])
    def test_normal(self, value, suffix, expected):
        assert command_to_filename(value, suffix) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [1, AttributeError],
        [None, AttributeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            command_to_filename(value)


class Test_compare_version:

    @pytest.mark.parametrize(['lhs', 'rhs', "expected"], [
        ["1.0.0", "1.0.0", 0],

        ["1.0.0", "0.9.9", 1],
        ["1.1.0", "1.0.9", 1],
        ["1.0.1", "1.0.0", 1],

        ["0.9.9", "1.0.0", -1],
        ["1.0.9", "1.1.0", -1],
        ["1.0.0", "1.0.1", -1],
    ])
    def test_normal(self, lhs, rhs, expected):
        assert compare_version(lhs, rhs) == expected

    @pytest.mark.parametrize(['lhs', 'rhs', "expected"], [
        [None, None, AttributeError],
        ["1.0.0", None, AttributeError],
        [None, "1.0.0", AttributeError],
        [1, "1.0.0", AttributeError],
        [nan, "1.0.0", AttributeError],
        [True, "1.0.0", AttributeError],
        ["aaa", "1.0.0", ValueError],
        ["1.0.0", "aaa", ValueError],
        ["1.2.3.4", "1.0.0", ValueError],
        ["1.0.0", "1.2.3.4", ValueError],
    ])
    def test_exception(self, lhs, rhs, expected):
        with pytest.raises(expected):
            compare_version(lhs, rhs)


class Test_get_execution_command:

    def test_normal(self):
        assert dataproperty.is_not_empty_string(get_execution_command())


class Test_sleep_wrapper:

    @pytest.mark.parametrize(["value", "dry_run", "expected"], [
        [0.1, False, 0.1],
        [-1, False, 0],
        [0.1, True, 0],
    ])
    def test_normal(self, value, dry_run, expected):
        sleep_wrapper(value, dry_run) == expected

    @pytest.mark.parametrize(["value", "dry_run"], [
    ])
    def test_abnormal(self, value, dry_run):
        sleep_wrapper(value, dry_run)

    @pytest.mark.parametrize(["value", "dry_run", "expected"], [
        [None, True, TypeError],
        [None, False, TypeError],
        ["a", True, ValueError],
        ["a", False, ValueError],
        [inf, True, OverflowError],
        [inf, False, OverflowError],
        [nan, True, IOError],
        [nan, False, IOError],
    ])
    def test_exception(self, value, dry_run, expected):
        with pytest.raises(expected):
            sleep_wrapper(value, dry_run)


class Test_dump_dict:

    @pytest.mark.parametrize(["value", "expected"], [
        [
            {"a": 1},
            """{
    "a": 1
}""",
        ],
        [
            {"a": 1.0},
            """{
    "a": 1.0
}""",
        ],
        ["", "{}"],
    ])
    def test_normal(self, value, expected):
        assert dump_dict(value, indent=4) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [1, TypeError],
        [None, TypeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            assert dump_dict(value)
