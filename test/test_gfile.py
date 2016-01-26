'''
@author: Tsuyoshi Hombashi

:required:
    https://pypi.python.org/pypi/pytest
'''

import os
import itertools

import pytest
from path import Path

import thutils.common as common
from thutils.gfile import *


TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))

EMPTY_FILE_NAME = "empty_file"
TEMP_FILE_NAME = "tmp_file"
EMPTY_FILE_PATH = os.path.join(TEST_DIR_PATH, EMPTY_FILE_NAME + ".txt")
EMPTY_DIR_NAME = "empty_dir"
EMPTY_DIR_PATH = os.path.join(TEST_DIR_PATH, EMPTY_DIR_NAME)


class Test_FileManager_touch:

    @pytest.mark.parametrize(["value"], [
        ["aaa"],
        ["aaa/bbb"],
    ])
    def test_normal_file(self, tmpdir, value):
        FileManager.initialize(dry_run=False)
        target_dir = tmpdir.join("touch")
        target_path = os.path.join(str(target_dir), value)
        FileManager.touch(target_path)

    @pytest.mark.parametrize(["value"], [
        ["touch_time"],
    ])
    def test_normal_time(self, tmpdir, value):
        import time

        target_dir = tmpdir.join("touch")
        tmp_path = os.path.join(str(target_dir), value)

        FileManager.initialize(dry_run=False)

        touch_file = FileManager.touch(tmp_path)
        expected = Path(tmp_path)
        assert touch_file == expected
        before_atime = touch_file.atime
        time.sleep(0.5)
        touch_file = FileManager.touch(tmp_path)
        assert touch_file == expected
        assert touch_file.atime > before_atime


class Test_FileManager_make_directory:

    @pytest.mark.parametrize(["value"], [
        ["test_normal_1"],
    ])
    def test_normal_1(self, tmpdir, value):
        FileManager.initialize(dry_run=False)

        target_dir = tmpdir.join("make_directory")
        target_path = os.path.join(str(target_dir), value)

        assert not os.path.exists(target_path)
        assert FileManager.make_directory(target_path) == Path(target_path)
        assert os.path.isdir(target_path)

    @pytest.mark.parametrize(["value"], [
        ["test_normal_2"],
    ])
    def test_normal_2(self, tmpdir, value):
        FileManager.initialize(dry_run=False)

        target_dir = tmpdir.join("make_directory")
        target_path = os.path.join(str(target_dir), value)

        assert not os.path.exists(target_path)
        assert FileManager.make_directory(target_path) == Path(target_path)
        assert FileManager.make_directory(target_path) == Path(target_path)
        assert os.path.isdir(target_path)

    @pytest.mark.parametrize(["value", "expected"], [
        [None, NullPathError],
    ])
    def test_exception(self, tmpdir, value, expected):
        with pytest.raises(expected):
            FileManager.make_directory(value)


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
        [None, NullPathError],
        [1.1, NullPathError],
        [True, NullPathError],
        ["/test/aa:aa", InvalidFilePathError],
        ["/test/aa*aa", InvalidFilePathError],
        ["/test/aa?aa", InvalidFilePathError],
        ["/test/aa\"aa", InvalidFilePathError],
        ["/test/aa<aa", InvalidFilePathError],
        ["/test/aa>aa", InvalidFilePathError],
        ["/test/aa|aa", InvalidFilePathError],

        ["c:\\aa:aa", InvalidFilePathError],
        ["c:\\aa*aa", InvalidFilePathError],
        ["c:\\aa?aa", InvalidFilePathError],
        ["c:\\aa\"aa", InvalidFilePathError],
        ["c:\\aa<aa", InvalidFilePathError],
        ["c:\\aa>aa", InvalidFilePathError],
        ["c:\\aa|aa", InvalidFilePathError],
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
        [None, NullPathError],
        [1.1, NullPathError],
        [True, NullPathError],
        ["", NullPathError],
        ["/not/existing/file/__path__", FileNotFoundError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            assert check_file_existence(value)


class Test_sanitize_file_name:
    SANITIZE_CHAR_LIST = [
        "\\", ":", "*", "?", '"', "<", ">", "|",
    ]
    NOT_SANITIZE_CHAR_LIST = [
        "!", "#", "$", '&', "'", "_",
        "=", "~", "^", "@", "`", "[", "]", "+", ";", "{", "}",
        ",", ".", "(", ")", "%",
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
        assert sanitize_file_name(value, replace_text) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, AttributeError],
        [1, AttributeError],
        [True, AttributeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            sanitize_file_name(value)


class Test_replace_symbol:
    TARGET_CHAR_LIST = [
        "\\", ":", "*", "?", '"', "<", ">", "|",
        ",", ".", "%", "(", ")", "/", " ",
    ]
    NOT_TARGET_CHAR_LIST = [
        "!", "#", "$", '&', "'", "_",
        "=", "~", "^", "@", "`", "[", "]", "+", ";", "{", "}",
    ]
    REPLACE_TEXT_LIST = ["", "_"]

    @pytest.mark.parametrize(
        ["value", "replace_text", "expected"],
        [
            ["A" + c + "B", rep, "A" + rep + "B"] for c, rep in itertools.product(
                TARGET_CHAR_LIST, REPLACE_TEXT_LIST)
        ] + [
            ["A" + c + "B", rep, "A" + c + "B"] for c, rep in itertools.product(
                NOT_TARGET_CHAR_LIST, REPLACE_TEXT_LIST)
        ]
    )
    def test_normal_1(self, value, replace_text, expected):
        assert replace_symbol(value, replace_text) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, AttributeError],
        [1, AttributeError],
        [True, AttributeError],
    ])
    def test_abnormal(self, value, expected):
        with pytest.raises(expected):
            replace_symbol(value)


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
