# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required:
    https://pypi.python.org/pypi/pytest
'''

import os
import platform

import pytest

import thutils
from thutils.binary_writer import *


@pytest.fixture
def subproc_wrapper():
    return thutils.subprocwrapper.SubprocessWrapper()


@pytest.fixture
def bin_writer():
    return DummyBinaryDataWriter()


TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_FILE_NAME = "hoge"


class Test_BinaryWriter:

    @pytest.mark.parametrize(["io_size_byte"], [
        [1],
        [8 * 1024],
        [1 * 1024 ** 2],
        [10.2],  # 端数は切り捨てられる(io_size_byte==10)となる
        [True],  # io_size_byte==1と判断される
    ])
    def test_new(self, io_size_byte):
        DummyBinaryDataWriter(io_size_byte)

    @pytest.mark.parametrize(["io_size_byte", "expected"], [
        [None, TypeError],
        [0, ValueError],
        [-1, ValueError],
        [1024 ** 3, ValueError],
    ])
    def test_new_exception(self, tmpdir, io_size_byte, expected):
        with pytest.raises(expected):
            DummyBinaryDataWriter(io_size_byte)

    @pytest.mark.parametrize(["write_size", "expected"], [
        [None, TypeError],
        [-1, ValueError],
    ])
    def test_writeBinary_exception(
            self, tmpdir, write_size, expected):

        write_path = str(tmpdir.join(TEST_FILE_NAME))
        bin_writer = DummyBinaryDataWriter()

        with pytest.raises(expected):
            bin_writer.write_binary(
                file_path=write_path,
                write_size_byte=write_size)


class Test_LinuxBinaryWriter:

    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(["write_size", "expected"], [
        [1024 ** 2, 1024 ** 2],
    ])
    def test_normal(
            self, monkeypatch, tmpdir, write_size, expected):

        bin_writer = DummyBinaryDataWriter()

        write_path = str(tmpdir.join(TEST_FILE_NAME))
        assert not os.path.isfile(write_path)
        assert bin_writer.write_binary(
            file_path=write_path,
            write_size_byte=write_size) == expected
        assert os.path.isfile(write_path)
        assert os.path.getsize(write_path) == write_size


class Test_WindowsBinaryWriter:

    @pytest.mark.skipif("platform.system() == 'Linux'")
    @pytest.mark.parametrize(["write_size", "expected"], [
        [1024 ** 2, 1024 ** 2],
    ])
    def test_normal(
            self, monkeypatch, tmpdir, write_size, expected):

        os.O_BINARY = 32768
        os.O_SEQUENTIAL = 32

        bin_writer = DummyBinaryDataWriter()

        write_path = str(tmpdir.join(TEST_FILE_NAME))
        assert not os.path.isfile(write_path)
        assert bin_writer.write_binary(
            file_path=write_path,
            write_size_byte=write_size) == expected
        assert os.path.isfile(write_path)
        assert os.path.getsize(write_path) == write_size
