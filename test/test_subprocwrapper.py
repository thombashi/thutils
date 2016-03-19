# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required: py.test
'''

import errno
import os
import platform
from subprocess import PIPE

import dataproperty
import pytest
import six

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
    return SubprocessWrapper()


@pytest.fixture
def subproc_dryrun():
    return SubprocessWrapper()


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
    ])
    def test_normal(self, subproc_run, command, ignore_error_list, expected):
        assert subproc_run.run(command, ignore_error_list) == expected
        assert subproc_run.command == command

    @pytest.mark.parametrize(["command", "expected"], [
        ["echo test", "test"],
    ])
    def test_stdout(self, subproc_run, command, expected):
        assert subproc_run.run(command) == 0
        assert subproc_run.stdout_text.strip() == six.b(expected)

    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(["command", "ignore_error_list", "expected"], [
        ["", [], ValueError],
        [None, [], ValueError],
        ["not_exist_command", [], RuntimeError],
    ])
    def test_exception(self, subproc_run, command, ignore_error_list, expected):
        with pytest.raises(expected):
            subproc_run.run(command, ignore_error_list)


class Test_SubprocessWrapper_popen_command:

    @pytest.mark.parametrize(["command", "std_in", "environ", "expected"], [
        ["hostname", None, None, 0],
        ["hostname", None, dict(os.environ), 0],
    ])
    def test_normal(self, subproc_run, command, std_in, environ, expected):
        proc = subproc_run.popen_command(command, std_in, environ)
        ret_stdout, ret_stderr = proc.communicate()
        assert dataproperty.is_not_empty_string(ret_stdout)
        assert dataproperty.is_empty_string(ret_stderr)
        assert proc.returncode == expected

    @pytest.mark.skipif("platform.system() == 'Windows'")
    @pytest.mark.parametrize(["command", "input", "environ", "expected"], [
        ["grep a", "aaa", None, 0],
    ])
    def test_normal_stdin(self, subproc_run, command, input, environ, expected):
        proc = subproc_run.popen_command(command, PIPE, environ)
        ret_stdout, ret_stderr = proc.communicate(input=six.b(input))
        assert dataproperty.is_not_empty_string(ret_stdout)
        assert dataproperty.is_empty_string(ret_stderr)
        assert proc.returncode == expected
