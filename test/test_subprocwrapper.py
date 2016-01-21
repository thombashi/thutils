# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required: py.test
'''

import os
from subprocess import PIPE

import pytest
import six

import thutils
from thutils.syswrapper import SubprocessWrapper


@pytest.fixture
def subproc_run():
    return thutils.syswrapper.SubprocessWrapper()


@pytest.fixture
def subproc_dryrun():
    return thutils.syswrapper.SubprocessWrapper()


class Test_SubprocessWrapper_init:

    @pytest.mark.parametrize(["dryrun"], [
        [True],
        [False],
    ])
    def test_normal(self, dryrun):
        assert SubprocessWrapper(dryrun) is not None


class Test_SubprocessWrapper_run:

    @pytest.mark.parametrize(["command", "ignore_error_list", "expected"], [
        ["ls", [], 0],
        ["ls", None, 0],
        ["ls", [2], 0],
        ["ls not_exist_dir", [], 2],
        ["ls not_exist_dir", [2], 2],
        ["not_exist_command", [], -1],
        ["", [], -1],
        [None, [], -1],
    ])
    def test_normal(self, subproc_run, command, ignore_error_list, expected):
        assert subproc_run.run(command, ignore_error_list) == expected


class Test_SubprocessWrapper_popen_command:

    @pytest.mark.parametrize(["command", "std_in", "environ", "expected"], [
        ["hostname", None, None, 0],
        ["hostname", None, dict(os.environ), 0],
    ])
    def test_normal(self, subproc_run, command, std_in, environ, expected):
        proc = subproc_run.popen_command(command, std_in, environ)
        ret_stdout, ret_stderr = proc.communicate()
        assert thutils.common.is_not_empty_string(ret_stdout)
        assert thutils.common.is_empty_string(ret_stderr)
        assert proc.returncode == expected

    @pytest.mark.parametrize(["command", "input", "environ", "expected"], [
        ["grep a", "aaa", None, 0],
    ])
    def test_normal_stdin(self, subproc_run, command, input, environ, expected):
        proc = subproc_run.popen_command(command, PIPE, environ)
        ret_stdout, ret_stderr = proc.communicate(input=six.b(input))
        assert thutils.common.is_not_empty_string(ret_stdout)
        assert thutils.common.is_empty_string(ret_stderr)
        assert proc.returncode == expected
