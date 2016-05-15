'''
@author: Tsuyoshi Hombashi
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
        [None, ValueError],
    ])
    def test_exception(self, tmpdir, value, expected):
        with pytest.raises(expected):
            FileManager.make_directory(value)


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
        [None, ValueError],
        [1.1, ValueError],
        [True, ValueError],
        ["", ValueError],
        ["/not/existing/file/__path__", FileNotFoundError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            assert check_file_existence(value)


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
