# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required:
    https://pypi.python.org/pypi/pytest
'''

import os

import pytest

import thutils
from thutils.main import *
import thutils.common as common
import thutils.gfile as gfile


@pytest.fixture
def subproc_wrapper():
    return thutils.subprocwrapper.SubprocessWrapper()

TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


def return0_func():
    return 0


def return1_func():
    return 1


def raise_InvalidFilePathError():
    raise gfile.InvalidFilePathError()


def raise_FileNotFoundError():
    raise gfile.FileNotFoundError()


def raise_IOError():
    raise IOError()


def raise_ValueError():
    raise ValueError()


def raise_ImportError():
    raise ImportError()


def raise_KeyboardInterrupt():
    raise KeyboardInterrupt


class Test_Main:

    @pytest.mark.parametrize(["value", "expected"], [
        [return0_func, 0],
        [return1_func, 1],
        [raise_InvalidFilePathError, EX_NOINPUT],
        [raise_FileNotFoundError, EX_NOINPUT],
        [raise_IOError, EX_IOERR],
        [raise_ValueError, EX_SOFTWARE],
        [raise_ImportError, EX_OSFILE],
        [raise_KeyboardInterrupt, 1],
    ])
    def test_normal(self, value, expected):
        main = Main(value)
        assert main() == expected

    @pytest.mark.parametrize(["value", "args", "expected"], [
        [None, None, TypeError],
    ])
    def test_exception(self, value, args, expected):
        with pytest.raises(expected):
            main = Main(value, args)
            main()
