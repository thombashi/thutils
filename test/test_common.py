# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required:
    https://pypi.python.org/pypi/pytest
'''

import platform

import pytest

from thutils.common import *
from thutils.gfile import *
from thutils.sqlite import *

nan = float("nan")
inf = float("inf")


def testStr():
    assert str(0) == "0"
    assert str(0.0) == "0.0"
    assert str(0.00) == "0.0"
    assert str(0.1) == "0.1"
    assert str(0.10) == "0.1"


def return0_func():
    return 0


class Test_isInteger:

    @pytest.mark.parametrize(["value"], [
        [0], [99999999999], [-99999999999],
        [1234567890123456789], [-1234567890123456789],
        ["0"], ["99999999999"], ["-99999999999"],
        [" 1"], ["1 "],
    ])
    def test_normal(self, value):
        assert is_integer(value)

    @pytest.mark.parametrize(["value"], [
        [None], [nan], [inf],
        [0.5], ["0.5"],
        [""], ["test"], ["1a1"], ["11a"], ["a11"],
        #["１"],
        [True],
        [1e-05], [-1e-05],
        ["1e-05"], ["-1e-05"],
        [-0.00001],
    ])
    def test_abnormal(self, value):
        assert not is_integer(value)


class Test_isHex:

    @pytest.mark.parametrize(["value"], [
        ["0x00"], ["0xffffffff"], ["a"], ["f"],
    ])
    def test_normal(self, value):
        assert is_hex(value)

    @pytest.mark.parametrize(["value"], [
        [None], [nan], [inf],
        [0], [1], [0.5],
        ["test"], ["g"],
        #["１"],
        [True],
    ])
    def test_abnormal(self, value):
        assert not is_hex(value)


class Test_is_float:

    @pytest.mark.parametrize(["value"], [
        [0.0], [0.1], [-0.1], [1], [-1],
        ["0.0"], ["0.1"], ["-0.1"], ["1"], ["-1"],
        [.5], [0.],
        ["1e-05"],
        [nan], [inf],
    ])
    def test_normal(self, value):
        assert is_float(value)

    @pytest.mark.parametrize(["value"], [
        [None],
        ["test"],
        ["inf"],
        #["１"],
        [True],
    ])
    def test_abnormal(self, value):
        assert not is_float(value)


class Test_isNaN:

    @pytest.mark.parametrize(["value", "expected"], [
        [nan, True],

        [None, False],
        ["nan", False],
        ["１", False],
        [inf, False],
        [1, False],
        [0.1, False],
        [True, False],
    ])
    def test_normal(self, value, expected):
        assert is_nan(value) == expected


class Test_isNotEmptyString:

    @pytest.mark.parametrize(["value", "expected"], [
        ["nan", True],
        ["テスト", True],

        [None, False],
        ["", False],
        ["  ", False],
        ["\t", False],
        ["\n", False],
        [[], False],
        [1, False],
        [True, False],
    ])
    def test_normal(self, value, expected):
        assert is_not_empty_string(value) == expected


class Test_isEmptyString:

    @pytest.mark.parametrize(["value", "expected"], [
        ["nan", False],
        ["テスト", False],

        [None, True],
        ["", True],
        ["  ", True],
        ["\t", True],
        ["\n", True],
        [True, True],
        [[], True],
        [1, True],
    ])
    def test_normal(self, value, expected):
        assert is_empty_string(value) == expected


class Test_isList:

    @pytest.mark.parametrize(["value"], [
        [[]],
        [[1]],
        [["a", "b"]],
        [["a"] * 200000],
    ])
    def test_normal(self, value):
        assert isList(value)

    @pytest.mark.parametrize(["value"], [
        [None], [()],
        [nan], [0], ["aaa"],
        [True],
    ])
    def test_abnormal(self, value):
        assert not isList(value)


class Test_isTuple:

    @pytest.mark.parametrize(["value"], [
        [()],
        [(1,)],
        [("a", "b")],
        [("a",) * 200000],
    ])
    def test_normal(self, value):
        assert isTuple(value)

    @pytest.mark.parametrize(["value"], [
        [None], [[]],
        [nan], [0], ["aaa"],
        [True],
    ])
    def test_abnormal(self, value):
        assert not isTuple(value)


class Test_isListOrTuple:

    @pytest.mark.parametrize(["value", "expected"], [
        [[], True],
        [[1], True],
        [["a"] * 200000, True],
        [(), True],
        [(1,), True],
        [("a",) * 200000, True],

        [None, False],
        [nan, False],
        [0, False],
        ["aaa", False],
        [True, False],
    ])
    def test_normal(self, value, expected):
        assert isListOrTuple(value) == expected


class Test_isEmptyList:

    @pytest.mark.parametrize(["value", "expected"], [
        [[], True],
        [None, True],

        [[1], False],
        [["a"] * 200000, False],
    ])
    def test_normal(self, value, expected):
        assert isEmptyList(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [(), False],
        [(1, 2), False],
        [nan, False],
        [0, False],
        ["aaa", False],
        [True, False],
    ])
    def test_abnormal(self, value, expected):
        assert isEmptyList(value) == expected


class Test_isEmptyTuple:

    @pytest.mark.parametrize(["value", "expected"], [
        [(), True],
        [None, True],

        [(1,), False],
        [("a",) * 200000, False],
    ])
    def test_normal(self, value, expected):
        assert isEmptyTuple(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [[], False],
        [[1, 2], False],
        [nan, False],
        [0, False],
        ["aaa", False],
        [True, False],
    ])
    def test_abnormal(self, value, expected):
        assert isEmptyTuple(value) == expected


class Test_isEmptyListOrTuple:

    @pytest.mark.parametrize(["value", "expected"], [
        [(), True],
        [[], True],
        [None, True],

        [[1], False],
        [["a"] * 200000, False],
        [(1,), False],
        [("a",) * 200000, False],
    ])
    def test_normal(self, value, expected):
        assert isEmptyListOrTuple(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [nan, False],
        [0, False],
        ["aaa", False],
        [True, False],
    ])
    def test_abnormal(self, value, expected):
        assert isEmptyListOrTuple(value) == expected


class Test_isNotEmptyListOrTuple:

    @pytest.mark.parametrize(["value", "expected"], [
        [(), False],
        [[], False],
        [None, False],

        [[1], True],
        [["a"] * 200000, True],
        [(1,), True],
        [("a",) * 200000, True],
    ])
    def test_normal(self, value, expected):
        assert isNotEmptyListOrTuple(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [nan, False],
        [0, False],
        ["aaa", False],
        [True, False],
    ])
    def test_abnormal(self, value, expected):
        assert isNotEmptyListOrTuple(value) == expected


class Test_isInstallCommand:

    @pytest.mark.parametrize(["value", "expected"], [
        ["ls", True],
        ["テスト", False],
        ["__not_existing_command__", False],
    ])
    def test_linux_normal(self, value, expected):
        assert is_install_command(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        ["", IndexError],
    ])
    def test_linux_normal(self, value, expected):
        with pytest.raises(expected):
            is_install_command(value)

    @pytest.mark.parametrize(["value", "expected"], [
        ["dir", False],
    ])
    def test_windows(self, monkeypatch, value, expected):
        def mockreturn():
            return "Windows"

        monkeypatch.setattr(platform, 'system', mockreturn)

        assert is_install_command(value) == expected


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
        assert is_nan(safe_division(dividend, divisor))

    @pytest.mark.parametrize(['dividend', "divisor", "expected"], [
        [inf, 2, inf],
        [-inf, 2, -inf],
        [2, inf, 0],
        [2, -inf, 0],
    ])
    def test_abnormal_2(self, dividend, divisor, expected):
        assert safe_division(dividend, divisor) == expected


class Test_get_list_item:
    input_list = [1, 2, 3]

    @pytest.mark.parametrize(['input_list', "index", "expected"], [
        [input_list, 0, 1],
        [input_list, 2, 3],

        [input_list, -1, None],
        [input_list, 4, None],

        [input_list, 1.0, None],
        [input_list, True, None],
        [input_list, None, None],
        [input_list, nan, None],
        [input_list, inf, None],
    ])
    def test(self, input_list, index, expected):
        assert get_list_item(input_list, index) == expected


class Test_get_integer_digit:

    @pytest.mark.parametrize(["value", "expected"], [
        [0, 1], [-0, 1],
        [1.01, 1], [-1.01, 1],
        [9.99, 1], [-9.99, 1],
        ["9.99", 1], ["-9.99", 1],
        ["0", 1], ["-0", 1],

        [10, 2], [-10, 2],
        [99.99, 2], [-99.99, 2],
        ["10", 2], ["-10", 2],
        ["99.99", 2], ["-99.99", 2],

        [100, 3], [-100, 3],
        [999.99, 3], [-999.99, 3],
        ["100", 3], ["-100", 3],
        ["999.99", 3], ["-999.99", 3],

        [10000000000000000000, 20], [-10000000000000000000, 20],
        [99999999999999099999.99, 20], [-99999999999999099999.99, 20],
        ["10000000000000000000", 20], ["-10000000000000000000", 20],
        ["99999999999999099999.99", 20], ["-99999999999999099999.99", 20],

        [True, 1],
        [False, 1],
    ])
    def test_normal(self, value, expected):
        assert get_integer_digit(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [99999999999999999999.99, 21],
        [-99999999999999999999.99, 21],
        ["99999999999999999999.99", 21],
        ["-99999999999999999999.99", 21],
    ])
    def test_abnormal(self, value, expected):
        # expected result == 20
        assert get_integer_digit(value) == expected

    @pytest.mark.parametrize(["value", 'exception'], [
        [None, TypeError],
        ["test", ValueError],
        ["a", ValueError],
        ["0xff", ValueError],
        [nan, ValueError],
        [inf, OverflowError],
    ])
    def test_exception(self, value, exception):
        with pytest.raises(exception):
            get_integer_digit(value)


"""
class Test_getFloatDigit:

    @pytest.mark.parametrize(["value", "expected"], [
        [0, 0], [-0, 0],
        [1000, 0], [-1000, 0],
        [1000.0, 0], [-1000.0, 0],

        [0.0, 1], [-0.0, 1],
        [0.10, 1], [-0.10, 1],
        [0.9, 1], [-0.9, 1],
        [10.1, 1], [-10.1, 1],
        [100.1, 1], [-100.1, 1],

        [0.01, 2], [-0.01, 2],
        [0.99, 2], [-0.99, 2],
        [99.999, 2], [-99.999, 2],

        [0.001, 3], [-0.001, 3],
        [9.999, 3], [-9.999, 3],
        [9.9999, 3], [-9.9999, 3],

        [0.0123, 4], [-0.0123, 4],
        [0.01234, 4], [-0.01234, 4],

        [1.0, 1],
    ])
    def test_normal(self, value, expected):
        assert getFloatDigit(value, get_integer_digit(value)) == expected

    @pytest.mark.parametrize(["value", 'significant_digit', "expected"], [
        [None, 1, TypeError],
        [nan, 1, ValueError],
        [inf, 1, ValueError],

        [1.0, None, TypeError],
        [None, None, TypeError],
        [nan, None, TypeError],
        [inf, None, TypeError],
    ])
    def test_abnormal(self, value, significant_digit, expected):
        with pytest.raises(expected):
            getFloatDigit(value, significant_digit)
"""


class Test_get_number_of_digit:

    @pytest.mark.parametrize(["value", "expected"], [
        [0, (1, 0)],
        [-0, (1, 0)],
        ["0", (1, 0)],
        ["-0", (1, 0)],
        [10, (2, 0)],
        [-10, (2, 0)],
        ["10", (2, 0)],
        ["-10", (2, 0)],
        [10.1, (2, 1)],
        [-10.1, (2, 1)],
        ["10.1", (2, 1)],
        ["-10.1", (2, 1)],
        [0.1, (1, 1)],
        [-0.1, (1, 1)],
        ["0.1", (1, 1)],
        ["-0.1", (1, 1)],
        [0.01, (1, 2)],
        [-0.01, (1, 2)],
        ["0.01", (1, 2)],
        ["-0.01", (1, 2)],
        [0.001, (1, 3)],
        [-0.001, (1, 3)],
        ["0.001", (1, 3)],
        ["-0.001", (1, 3)],
        [0.0001, (1, 4)],
        [-0.0001, (1, 4)],
        ["0.0001", (1, 4)],
        ["-0.0001", (1, 4)],
        [0.00001, (1, 4)],
        [-0.00001, (1, 4)],
        ["0.00001", (1, 4)],
        ["-0.00001", (1, 4)],
        [2e-05, (1, 4)],
        [-2e-05, (1, 4)],
        ["2e-05", (1, 4)],
        ["-2e-05", (1, 4)],
    ])
    def test_normal(self, value, expected):
        assert get_number_of_digit(value) == expected

    @pytest.mark.parametrize(["value", "expected1", "expected2"], [
        [True, 1, 1],
    ])
    def test_annormal(self, value, expected1, expected2):
        sig_digit, float_digit = get_number_of_digit(value)
        assert sig_digit == expected1
        assert float_digit == expected2

    @pytest.mark.parametrize(["value"], [
        [None],
        ["0xff"], ["test"], ["テスト"],
    ])
    def test_abnormal(self, value):
        sig_digit, float_digit = get_number_of_digit(value)
        assert is_nan(sig_digit)
        assert is_nan(float_digit)


class Test_getTextLen:

    def test_normal_1(self):
        assert get_text_len("") == 0
        assert get_text_len(
            "aaaaaaaaaaaaaaaaaaaa"
            "aaaaaaaaaaaaaaaaaaaa"
            "aaaaaaaaaaaaaaaaaaaa"
            "aaaaaaaaaaaaaaaaaaaa"
            "aaaaaaaaaaaaaaaaaaaa"
        ) == 100

    def test_normal_2(self):
        assert get_text_len(u"あ") == 1

    def test_abnormal_1(self):
        assert get_text_len(None) == 4

    def test_abnormal_2(self):
        assert get_text_len(nan) == 3
        assert get_text_len(inf) == 3


class Test_convertValue:

    def test_normal_1(self):
        assert convertValue("0") == 0
        assert convertValue("9999999999") == 9999999999
        assert convertValue("-9999999999") == -9999999999
        assert convertValue(0) == 0
        assert convertValue(9999999999) == 9999999999
        assert convertValue(-9999999999) == -9999999999

    def test_normal_2(self):
        assert convertValue("0.0") == 0
        assert convertValue(0.0) == 0

    def test_normal_3(self):
        assert convertValue("aaaaa") == "aaaaa"

    def test_abnormal_1(self):
        assert convertValue(None) is None

    def test_abnormal_2(self):
        assert is_nan(convertValue(nan))
        assert convertValue(inf) == inf


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


class Test_humanreadable_to_byte:

    @pytest.mark.parametrize(["value", "kilo_size", "expected"], [
        ["2b", 1024, 2],
        ["2 b", 1024, 2],
        ["2 B", 1024, 2],
        ["2k", 1024, 2 * 1024 ** 1],
        ["2 k", 1024, 2 * 1024 ** 1],
        ["2 K", 1024, 2 * 1024 ** 1],
        ["2m", 1024, 2 * 1024 ** 2],
        ["2 m", 1024, 2 * 1024 ** 2],
        ["2 M", 1024, 2 * 1024 ** 2],
        ["2g", 1024, 2 * 1024 ** 3],
        ["2 g", 1024, 2 * 1024 ** 3],
        ["2 G", 1024, 2 * 1024 ** 3],
        ["2t", 1024, 2 * 1024 ** 4],
        ["2 t", 1024, 2 * 1024 ** 4],
        ["2 T", 1024, 2 * 1024 ** 4],
        ["2p", 1024, 2 * 1024 ** 5],
        ["2 p", 1024, 2 * 1024 ** 5],
        ["2 P", 1024, 2 * 1024 ** 5],
        ["2.5 M", 1024, int(2.5 * 1024 ** 2)],
        ["2.5 m", 1024, int(2.5 * 1024 ** 2)],
        ["2b", 1000, 2],
        ["2 b", 1000, 2],
        ["2 B", 1000, 2],
        ["2k", 1000, 2 * 1000 ** 1],
        ["2 k", 1000, 2 * 1000 ** 1],
        ["2 K", 1000, 2 * 1000 ** 1],
        ["2m", 1000, 2 * 1000 ** 2],
        ["2 m", 1000, 2 * 1000 ** 2],
        ["2 M", 1000, 2 * 1000 ** 2],
        ["2g", 1000, 2 * 1000 ** 3],
        ["2 g", 1000, 2 * 1000 ** 3],
        ["2 G", 1000, 2 * 1000 ** 3],
        ["2t", 1000, 2 * 1000 ** 4],
        ["2 t", 1000, 2 * 1000 ** 4],
        ["2 T", 1000, 2 * 1000 ** 4],
        ["2p", 1000, 2 * 1000 ** 5],
        ["2 p", 1000, 2 * 1000 ** 5],
        ["2 P", 1000, 2 * 1000 ** 5],
        ["2.5 M", 1000, int(2.5 * 1000 ** 2)],
        ["2.5 m", 1000, int(2.5 * 1000 ** 2)],
    ])
    def test_normal(self, value, kilo_size, expected):
        assert humanreadable_to_byte(value, kilo_size) == expected

    @pytest.mark.parametrize(["value", "exception"], [
        [None, TypeError],
        [True, TypeError],
        [nan, TypeError],
        ["a", ValueError],
        ["ｂ", ValueError],
        ["1k0 ", ValueError],
        ["10kb", ValueError],
    ])
    def test_exception(self, value, exception):
        with pytest.raises(exception):
            humanreadable_to_byte(value)


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


class Test_strtobool_wrapper:

    @pytest.mark.parametrize(["value", "expected"], [
        ["true", True],
        ["True", True],
        ["TRUE", True],
        ["false", False],
        ["False", False],
        ["FALSE", False],
    ])
    def test_normal(self, value, expected):
        assert strtobool_wrapper(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        ["falsea", ValueError],
        ["aFalse", ValueError],
        ["aFALSEa", ValueError],
        ["Ｔｒｕｅ", ValueError],

        [1.0, TypeError],
        [None, TypeError],
        [nan, TypeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            strtobool_wrapper(value)


class Test_splitLineList:

    @pytest.mark.parametrize(["value", "separator", "expected"], [
        [
            ["a", "", "b", "c"],
            "",
            [["a"], ["b", "c"]]
        ],
        [
            ("a", "", "b", "c"),
            "",
            [["a"], ["b", "c"]]
        ],
        [
            ["a", "", "b", "c"],
            "b",
            [["a", ""], ["c"]]
        ],
        ["", "", []
         ],
    ])
    def test_normal(self, value, separator, expected):
        assert splitLineList(value, separator) == expected

    @pytest.mark.parametrize(["value", "separator", "expected"], [
        [None, "", TypeError],
        #["", "", TypeError],
        #[1, "", TypeError],
    ])
    def test_exception(self, value, separator, expected):
        with pytest.raises(expected):
            splitLineList(value, separator)


class Test_splitLineListByRe:

    @pytest.mark.parametrize(
        ["value", "separator", "is_include_matched_line", "expected"],
        [
            [
                ["abcdefg", "ABCDEFG", "1234"],
                re.compile("DEFG$"),
                False,
                [["abcdefg"], ["1234"]],
            ],
            [
                ["abcdefg", "ABCDEFG", "1234"],
                re.compile("DEFG$"),
                True,
                [["abcdefg"], ["ABCDEFG", "1234"]],
            ],
        ])
    def test_normal(self, value, separator, is_include_matched_line, expected):
        assert splitLineListByRe(
            value, separator, is_include_matched_line) == expected

    @pytest.mark.parametrize(["value", "separator", "expected"], [
        [None, "", TypeError],
        #["", "", TypeError],
        #[1, "", TypeError],
    ])
    def test_exception(self, value, separator, expected):
        with pytest.raises(expected):
            splitLineListByRe(value, separator)


class Test_checkInstallCommand:

    @pytest.mark.parametrize(["value"], [
        [[]],
    ])
    def test_normal(self, value):
        verify_install_command(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        ["__not_existing_command__", NotInstallError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            verify_install_command(value)


class Test_getFileNameFromCommand:

    @pytest.mark.parametrize(["value", "expected"], [
        ["/bin/ls", "bin-ls"],
        ["cat /proc/cpuinfo", "cat_-proc-cpuinfo"],
        ["", ""],
    ])
    def test_normal(self, value, expected):
        assert command_to_filename(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [1, AttributeError],
        [None, AttributeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            command_to_filename(value)


class Test_compareVersion:

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


class Test_sleepWrapper:

    @pytest.mark.parametrize(["value", "dry_run", "expected"], [
        [0.1, False, 0.1],
        [-1, False, 0],
        [0.1, True, 0],
        [inf, True, 0],
        [nan, True, 0],
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
        [inf, False, IOError],
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

    #"""
    @pytest.mark.parametrize(["value", "expected"], [
        [1, TypeError],
        [None, TypeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            assert dump_dict(value)
    #"""
