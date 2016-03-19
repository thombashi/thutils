# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required: py.test
'''

import re

import pytest
import six
from voluptuous import Schema, Required, Any, Range, Invalid, ALLOW_EXTRA

import thutils
from thutils.loader import JsonLoader


TEMP_FILE_NAME = "tmp.json"
TEST_JSON = """
{
    "comment"           : "comment",
    "operation"         : "write",
    "thread"            : 8,
    "io_size"           : "8k",
    "access_percentage" : 100
}
"""
TEST_JSON_B = six.b("""
{
    "comment"           : "comment",
    "operation"         : "write",
    "thread"            : 8,
    "io_size"           : "8k",
    "access_percentage" : 100
}
""")
TEST_JSON_U = six.u("""
{
    "comment"           : "comment",
    "operation"         : "write",
    "thread"            : 8,
    "io_size"           : "8k",
    "access_percentage" : 100
}
""")

EXPECTED = {
    "comment": "comment",
    "operation": "write",
    "thread": 8,
    "io_size": "8k",
    "access_percentage": 100
}


def validate_io_size(v):
    if re.search("^[0-9]+[bkm]", v) is None:
        raise Invalid("not a valid value (%s)" % str(v))

SCHEMA = Schema({
    "comment": six.text_type,
    Required("operation"): Any("read", "write"),
    "thread": Range(min=1),
    Required("io_size"): validate_io_size,
    Required("access_percentage"): Range(min=1, max=100),
}, extra=ALLOW_EXTRA)


class Test_JsonLoader_load:

    @pytest.mark.parametrize(["value", "schema", "expected"], [
        [
            TEST_JSON,
            None,
            EXPECTED,
        ],
        [
            TEST_JSON,
            SCHEMA,
            EXPECTED,
        ],
        [
            TEST_JSON_B,
            SCHEMA,
            EXPECTED,
        ],
        [
            TEST_JSON_U,
            SCHEMA,
            EXPECTED,
        ],
    ])
    def test_normal(self, tmpdir, value, schema, expected):
        p = tmpdir.join(TEMP_FILE_NAME)
        p.write(value)

        assert JsonLoader.load(str(p), schema) == expected

    @pytest.mark.parametrize(["value", "schema", "expected"], [
        [None, None, TypeError],
        ["{'a' : 1,}", None, ValueError],
    ])
    def test_exception(self, value, schema, expected):
        with pytest.raises(expected):
            JsonLoader.loads(value, schema)


class Test_JsonLoader_loads:

    @pytest.mark.parametrize(["value", "schema", "expected"], [
        [
            TEST_JSON,
            None,
            EXPECTED,
        ],
        [
            TEST_JSON,
            SCHEMA,
            EXPECTED,
        ],
    ])
    def test_normal(self, value, schema, expected):
        assert JsonLoader.loads(value, schema) == expected

    @pytest.mark.parametrize(["value", "schema", "expected"], [
        [None, None, TypeError],
        ["{'a' : 1,}", None, ValueError],
    ])
    def test_exception(self, value, schema, expected):
        with pytest.raises(expected):
            JsonLoader.loads(value, schema)
