# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required: py.test
'''

import logging
import sys

import pytest

from thutils.logger import logger


class Test_logger_initialize:

    @pytest.mark.parametrize(
        [
            "program_filename", "dry_run",
            "print_stack_trace", "with_no_log",
            "output_dir_path", "stdout_log_level",
            "expected_dir", "expected_file",
        ],
        [
            [
                "program", False,
                False, False, ".", logging.INFO,
                ".", "program.log"
            ],
            [
                "program", False,
                True, False, "tmp", logging.DEBUG,
                "tmp", "program.log"
            ],
            [
                "program", False,
                True, True, "out", logging.NOTSET,
                "", ""
            ],
        ]
    )
    def test_normal(
            self, program_filename, dry_run, print_stack_trace,
            with_no_log, output_dir_path, stdout_log_level,
            expected_dir, expected_file):
        import os.path

        log_path = logger.initialize(
            program_filename,
            dry_run,
            print_stack_trace,
            with_no_log,
            stdout_log_level,
            output_dir_path=output_dir_path,
        )
        assert log_path == os.path.join(expected_dir, expected_file)


class Test_logger_get_log_clear_log:

    def test_normal(self):
        logger.clear_log()
        assert len(logger.get_log()) == 0
        logger.info("a")
        assert len(logger.get_log()) == 1
        logger.clear_log()
        assert len(logger.get_log()) == 0


class Test_logger_write:

    @pytest.mark.parametrize(["message", "log_level", "caller"], [
        ["aaa", logging.DEBUG, None],
        ["aaa", logging.INFO, None],
        ["aaa", logging.WARN, None],
        ["aaa", logging.ERROR, None],
        ["aaa", logging.FATAL, None],
        ["aaa", logging.INFO, logging.getLogger().findCaller()],
        [None, logging.INFO, None],
    ])
    def test_smoke(self, message, log_level, caller):
        try:
            raise ValueError()
        except:
            logger.write(message, log_level, caller)

    @pytest.mark.parametrize(["message", "log_level", "expected"], [
        ["aaa", None, ValueError],
        [None, None, ValueError],
    ])
    def test_exception(self, message, log_level, expected):
        with pytest.raises(expected):
            logger.write(message, log_level)


class Test_logger_info:

    @pytest.mark.parametrize(["message", "caller"], [
        ["aaa", None],
    ])
    def test_smoke(self, message, caller):
        logger.info(message, caller)


class Test_logger_debug:

    @pytest.mark.parametrize(["message", "caller"], [
        ["aaa", None],
    ])
    def test_smoke(self, message, caller):
        logger.debug(message, caller)


class Test_logger_warn:

    @pytest.mark.parametrize(["message", "caller"], [
        ["aaa", None],
    ])
    def test_smoke(self, message, caller):
        logger.warn(message, caller)


class Test_logger_error:

    @pytest.mark.parametrize(["message", "caller"], [
        ["aaa", None],
    ])
    def test_smoke(self, message, caller):
        logger.error(message, caller)


class Test_logger_exception:

    @pytest.mark.parametrize(["message"], [
        ["aaa"],
    ])
    def test_smoke(self, message):
        try:
            raise ValueError("for logger test")
        except:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e, message)


class Test_logger_fatal:

    @pytest.mark.parametrize(["message", "caller"], [
        ["aaa", None],
    ])
    def test_smoke(self, message, caller):
        try:
            raise ValueError("for logger test")
        except:
            # Python3では例外を送出していないときにtraceback.print_exc()を呼ぶと
            # AttributeError: 'NoneType' object has no attribute '__context__'
            # が発生する
            logger.fatal(message, caller)
