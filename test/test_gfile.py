'''
@author: Tsuyoshi Hombashi

:required:
    https://pypi.python.org/pypi/pytest
'''

import os
import itertools

import pytest

import thutils.common as common
from thutils.gfile import *


TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

EMPTY_FILE_NAME = "empty_file"
TEMP_FILE_NAME = "tmp_file"
EMPTY_FILE_PATH = os.path.join(TEST_DIR_PATH, EMPTY_FILE_NAME + ".txt")
EMPTY_DIR_NAME = "empty_dir"
EMPTY_DIR_PATH = os.path.join(TEST_DIR_PATH, EMPTY_DIR_NAME)


class Test_validatePath:

    @pytest.mark.parametrize(["value"], [
        ["/not/existing/file/__path__/"],
        ["/not/existing/file/__path__"],
        [
            "/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            "/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            "/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            "/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            "/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            "/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            "/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        ],
    ])
    def test_normal(self, value):
        validate_path(value)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, InvalidFilePathError],
        [1.1, InvalidFilePathError],
        [True, InvalidFilePathError],

        ["", InvalidFilePathError],
        ["/", InvalidFilePathError],
        ["//", InvalidFilePathError],
        ["..", InvalidFilePathError],
        ["../..", InvalidFilePathError],
        ["../../..", InvalidFilePathError],
        ["../../.././.././", InvalidFilePathError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            validate_path(value)


class Test_check_file_existence:

    def test_normal_file(self, tmpdir):
        p = tmpdir.join(TEMP_FILE_NAME)
        p.write("test contents")
        assert check_file_existence(str(p)) == FileType.FILE

    def test_normal_empty_file(self, tmpdir):
        p = tmpdir.join(EMPTY_FILE_NAME)
        p.write("")

        check_file_existence(str(p))

    @pytest.mark.parametrize(["value", "expected"], [
        [EMPTY_DIR_NAME, FileType.DIRECTORY],
    ])
    def test_normal_dir(self, tmpdir, value, expected):
        tmpdir.mkdir(value)
        assert check_file_existence(str(tmpdir)) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, InvalidFilePathError],
        [1.1, InvalidFilePathError],
        [True, InvalidFilePathError],
        ["", InvalidFilePathError],
        ["/not/existing/file/__path__", FileNotFoundError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            assert check_file_existence(value)


class Test_getFileNameFromPath:

    @pytest.mark.parametrize(["value", "expected"], [
        [EMPTY_FILE_PATH, EMPTY_FILE_NAME],
        [EMPTY_DIR_PATH, EMPTY_DIR_NAME],
        ["/not/existing/file/__path__", "__path__"],
        ["/not/existing/file/__path__/", "__path__"],
        ["/not/existing/file/__path__/ ", "__path__"],
        ["/__path__", "__path__"],
        ["__path__", "__path__"],
    ])
    def test_normal(self, value, expected):
        assert getFileNameFromPath(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        ["", ""],
    ])
    def test_abnormal(self, value, expected):
        assert getFileNameFromPath(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, AttributeError],
        [1, AttributeError],
        [True, AttributeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            assert getFileNameFromPath(value)


class Test_sanitizeFileName:
    SANITIZE_CHAR_LIST = [
        "\\", ":", "/", "*", "?", '"', "<", ">", "|",
    ]
    NOT_SANITIZE_CHAR_LIST = [
        "!", "#", "$", "%", '&', "'", "_",
        "=", "~", "^", "@", "`", "[", "]", "+", ";", "{", "}",
        ",", ".", "(", ")",
    ]
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            ["A" + c + "B", rep, "A" + rep + "B"]
            for c, rep in itertools.product(
                SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ] + [
            ["A" + c + "B", rep, "A" + c + "B"]
            for c, rep in itertools.product(
                NOT_SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
    )
    def test_normal(self, value, replace_text, expected):
        assert sanitizeFileName(value, replace_text) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, AttributeError],
        [1, AttributeError],
        [True, AttributeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            sanitizeFileName(value)


class Test_adjustFileName:
    SANITIZE_CHAR_LIST = [
        "\\", ":", "/", "*", "?", '"', "<", ">", "|",
        ",", ".", "%", "(", ")",
    ]
    NOT_SANITIZE_CHAR_LIST = [
        "!", "#", "$", '&', "'", "_",
        "=", "~", "^", "@", "`", "[", "]", "+", ";", "{", "}",
    ]
    REPLACE_TEXT_LIST = [""]

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["A" + c + "B", "A" + rep + "B"] for c, rep in itertools.product(
                SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ] + [
            ["A" + c + "B", "A" + c + "B"] for c, rep in itertools.product(
                NOT_SANITIZE_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
    )
    def test_normal_1(self, value, expected):
        assert adjustFileName(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        ["A B", "A_B"],
    ])
    def test_normal_2(self, value, expected):
        assert adjustFileName(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, AttributeError],
        [1, AttributeError],
        [True, AttributeError],
    ])
    def test_abnormal(self, value, expected):
        with pytest.raises(expected):
            adjustFileName(value)


class Test_parsePermission3Char:

    @pytest.mark.parametrize(["value", "expected"], [
        ["---", 0],
        ["--x", 1],
        ["-w-", 2],
        ["r--", 4],
        ["-wx", 3],
        ["r-x", 5],
        ["rw-", 6],
        ["rwx", 7],
    ])
    def test_normal(self, value, expected):
        assert parsePermission3Char(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        ["foo", 0],
    ])
    def test_abnormal(self, value, expected):
        assert parsePermission3Char(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [1, TypeError],
        [True, TypeError],
        ["hoge", ValueError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            parsePermission3Char(value)


def getTestValueList():
    perm_list = [
        ["---", 0],
        ["--x", 1],
        ["-w-", 2],
        ["r--", 4],
        ["-wx", 3],
        ["r-x", 5],
        ["rw-", 6],
        ["rwx", 7],
    ]

    return_value_list = []
    for pair_list in itertools.product(perm_list, perm_list, perm_list):
        value = "-"
        expected = ""
        for transposition_pair_list in zip(pair_list):
            for pair in transposition_pair_list:
                value += pair[0]
                expected += str(pair[1])

        return_value_list.append([value, int(expected, base=8)])

    return return_value_list


class Test_parseLsPermissionText:

    @pytest.mark.parametrize(["value", "expected"], getTestValueList())
    def test_normal(self, value, expected):
        assert parseLsPermissionText(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [1, TypeError],
        [True, TypeError],
        ["hoge", ValueError],
        ["aaaaaaaaaa", ValueError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            parseLsPermissionText(value)
