# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required: py.test
'''

import os

import pytest

import thutils
from thutils.option import *
from thutils.gtime import *


VERSION = "1.0.0"


@pytest.fixture
def parser():
    return ArgumentParserObject()


@pytest.fixture
def maked_parser():
    parser = ArgumentParserObject()
    parser.make(VERSION, "", "")
    return parser


class Test_ArgumentParserObject_make:

    @pytest.mark.parametrize(["version", "description", "epilog"], [
        [VERSION, "", ""],
        ["9.9.9", "description", "epilog"],
        [VERSION, None, None],
    ])
    def test_smoke(self, parser, version, description, epilog):
        parser.make(version, description, epilog)

    @pytest.mark.parametrize(["version", "description", "epilog", "expected"], [
        [None, None, None, TypeError],
        [None, "", "", TypeError],
        [1, "", "", TypeError],
    ])
    def test_exception(self, parser, version, description, epilog, expected):
        with pytest.raises(expected):
            parser.make(version, description, epilog)


class Test_ArgumentParserObject_add_argument_group:

    @pytest.mark.parametrize(["value"], [
        ["test"],
    ])
    def test_normal(self, maked_parser, value):
        assert maked_parser.add_argument_group(value) is not None

    @pytest.mark.parametrize(["value", "expected"], [
        [None, ValueError],
        ["", ValueError],
        [1, ValueError],
    ])
    def test_exception(self, maked_parser, value, expected):
        with pytest.raises(expected):
            maked_parser.add_argument_group(value)


class Test_ArgumentParserObject_add_dry_run_option:

    def test_smoke(self, maked_parser):
        maked_parser.add_dry_run_option()


class Test_ArgumentParserObject_add_run_option:

    def test_smoke(self, maked_parser):
        maked_parser.add_run_option()


class Test_ArgumentParserObject_add_sql_argument_group:

    def test_smoke(self, maked_parser):
        assert maked_parser.add_sql_argument_group() is not None


class Test_ArgumentParserObject_add_profile_argument_group:

    def test_smoke(self, maked_parser):
        assert maked_parser.add_profile_argument_group() is not None


class Test_ArgumentParserObject_add_time_argument_group:

    def test_smoke(self, maked_parser):
        assert maked_parser.add_time_argument_group() is not None


class Test_ArgumentParserObject_add_time_range_argument_group:

    @pytest.mark.parametrize(["start_time_help_msg", "end_time_help_msg"],
                             [
        ["", ""],
    ])
    def test_normal(
            self, maked_parser, start_time_help_msg, end_time_help_msg):
        maked_parser.add_time_range_argument_group(
            start_time_help_msg, end_time_help_msg)


class Test_ArgumentParserObject_addMakeArgumentGroup:

    def test_smoke(self, maked_parser):
        maked_parser.addMakeArgumentGroup()
