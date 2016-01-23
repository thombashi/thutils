# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required: py.test
'''

import errno
import os
import platform
from subprocess import PIPE

import pytest
import six

import thutils
from thutils.subprocwrapper import SubprocessWrapper

os_type = platform.system()
if os_type == "Linux":
    list_command = "ls"
    list_command_errno = errno.ENOENT
elif os_type == "Windows":
    list_command = "dir"
    list_command_errno = 1
else:
    raise NotImplementedError(os_type)


@pytest.fixture
def subproc_run():
    return thutils.subprocwrapper.SubprocessWrapper()


@pytest.fixture
def subproc_dryrun():
    return thutils.subprocwrapper.SubprocessWrapper()


class Test_SubprocessWrapper_init:

    @pytest.mark.parametrize(["dryrun"], [
        [True],
        [False],
    ])
    def test_normal(self, dryrun):
        assert SubprocessWrapper(dryrun) is not None


class Test_SubprocessWrapper_run:

    @pytest.mark.parametrize(["command", "ignore_error_list", "expected"], [
        [list_command, [], 0],
        [list_command, None, 0],
        [list_command, [list_command_errno], 0],
        [list_command + " not_exist_dir", [], list_command_errno],
        [list_command + " not_exist_dir",
            [list_command_errno], list_command_errno],
        ["not_exist_command", [], list_command_errno],
        ["", [], errno.ENOENT],
        [None, [], errno.ENOENT],
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

    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(["command", "input", "environ", "expected"], [
        ["grep a", "aaa", None, 0],
    ])
    def test_normal_stdin(self, subproc_run, command, input, environ, expected):
        proc = subproc_run.popen_command(command, PIPE, environ)
        ret_stdout, ret_stderr = proc.communicate(input=six.b(input))
        assert thutils.common.is_not_empty_string(ret_stdout)
        assert thutils.common.is_empty_string(ret_stderr)
        assert proc.returncode == expected
