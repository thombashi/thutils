'''
@author: Tsuyoshi Hombashi

:required:
    https://pypi.python.org/pypi/pytest
'''

import itertools
import os
import sqlite3

import pytest
from six.moves import range

from thutils.common import *
from thutils.sqlite import *
import thutils.gfile as gfile


nan = float("nan")
inf = float("inf")
TEST_TABLE_NAME = "test_table"
TEST_DB_NAME = "test_db"
TEST_DB_VERSION = "1.0.0"


class Test_SqlQuery_sanitize:
    SANITIZE_CHAR_LIST = [
        "%", "/", "(", ")", "[", "]", "<", ">", ".", ";",
        "'", "!", "\\", "#", " ", "-", "+", "=", "\n"
    ]

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            ["AAA%s" % (re.escape(c)), "AAA"] for c in SANITIZE_CHAR_LIST
        ] + [
            ["%sBBB" % (re.escape(c)), "BBB"] for c in SANITIZE_CHAR_LIST
        ] + [
            [
                "%a/b(c)d[e]f<g>h.i;j'k!l\\m#n _o-p+q=r\nstrvwxyz" +
                os.linesep,
                "abcdefghijklmn_opqrstrvwxyz"
            ]
        ]
    )
    def test_normal(self, value, expected):
        assert SqlQuery.sanitize(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [1, TypeError],
        [nan, TypeError],
        [True, TypeError],
    ])
    def test_abnormal(self, value, expected):
        with pytest.raises(expected):
            SqlQuery.sanitize(value)


class Test_to_table_str:

    @pytest.mark.parametrize(["value", "expected"], [
        ["test", "test"],
        ["te%st", "[te%st]"],
        ["te(st", "[te(st]"],
        ["te)st", "[te)st]"],
        ["te-st", "[te-st]"],
        ["te+st", "[te+st]"],
        ["te.st", "[te.st]"],
        ["te st", "'te st'"],
    ])
    def test_normal(self, value, expected):
        assert SqlQuery.to_table_str(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [1, TypeError],
        [False, TypeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            assert SqlQuery.to_table_str(value)


class Test_to_attr_str:

    @pytest.mark.parametrize(["value", "operation", "expected"], [
        ["test", None, "test"],
        ["test", "AVG", "AVG(test)"],
        ["attr_a", 2, "attr_a"],
        ["attr_a", True, "attr_a"],
    ] + [
        ["te%sst" % (re.escape(c)), None, "[te%sst]" % (re.escape(c))]
        for c in [
            "%", "(", ")", ".", " ", "-", "+", "#"
        ] + [str(n) for n in range(10)]
    ]
    )
    def test_normal(self, value, operation, expected):
        assert SqlQuery.to_attr_str(value, operation) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [1, TypeError],
        [False, TypeError],
    ])
    def test_exception_1(self, value, expected):
        with pytest.raises(expected):
            SqlQuery.to_attr_str(value)


class Test_to_attr_str_list:

    @pytest.mark.parametrize(
        ["value", "operation", "expected"],
        [
            [
                ["%aaa", "bbb", "ccc-ddd"],
                None,
                ["[%aaa]", "bbb", "[ccc-ddd]"],
            ],
            [
                ["%aaa", "bbb"],
                "SUM",
                ["SUM([%aaa])", "SUM(bbb)"],
            ],
            [[], None, []],
        ]
    )
    def test_normal(self, value, operation, expected):
        assert list(SqlQuery.to_attr_str_list(value, operation)) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [nan, TypeError],
        [True, TypeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            SqlQuery.to_attr_str_list(value)


class Test_to_value_str:

    @pytest.mark.parametrize(["value", "expected"], [
        [0, "0"],
        ["0", "0"],
        [1.1, "1.1"],
        ["test", "'test'"],
        ["te st", "'te st'"],
        [None, "NULL"],
        [False, "'False'"],
    ])
    def test_normal(self, value, expected):
        assert SqlQuery.to_value_str(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [nan, "nan"],
        [inf, "inf"],
    ])
    def test_abnormal(self, value, expected):
        assert SqlQuery.to_value_str(value) == expected


class Test_to_value_str_list:

    @pytest.mark.parametrize(
        ["value", "expected"],
        [
            [[0, "bbb", None], ["0", "'bbb'", "NULL"]],
            [[], []],
        ]
    )
    def test_normal(self, value, expected):
        assert list(SqlQuery.to_value_str_list(value)) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        [None, TypeError],
        [nan, TypeError],
    ])
    def test_exception(self, value, expected):
        with pytest.raises(expected):
            assert SqlQuery.to_value_str_list(value)


class Test_make_select:

    @pytest.mark.parametrize(
        ["select", "table", "where", "extra", "expected"],
        [
            ["A", "B", None, None, "SELECT A FROM B"],
            ["A", "B B", None, None, "SELECT A FROM 'B B'"],
            [
                "A", "B-B",
                SqlQuery.make_where("C", 1),
                None, "SELECT A FROM [B-B] WHERE C = 1"
            ],
            ["A", "B-B", SqlQuery.make_where("C", 1, ">"), "ORDER BY D",
             "SELECT A FROM [B-B] WHERE C > 1 ORDER BY D"],
        ])
    def test_normal(self, select, table, where, extra, expected):
        assert SqlQuery.make_select(select, table, where, extra) == expected

    @pytest.mark.parametrize(
        ["select", "table", "where", "extra", "expected"], [
            ["A", None, None, None, ValueError],
            [None, None, None, None, ValueError],
            [None, "B", None, None, TypeError],
            [nan, None, None, None, ValueError],
            [nan, nan, None, None, ValueError],
            [nan, nan, nan, None, ValueError],
            [nan, nan, nan, nan, ValueError],
        ])
    def test_exception(self, select, table, where, extra, expected):
        with pytest.raises(expected):
            SqlQuery.make_select(select, table, where, extra)


class Test_make_insert:

    @pytest.mark.parametrize(["table", "insert_tuple", "is_isert_many", "expected"], [
        ["A", ["B"], False, "insert into A values (B)"],
        ["A", ["B", "C"], False, "insert into A values (B,C)"],
        ["A", ["B"], True, "insert into A values (?)"],
        ["A", ["B", "C"], True, "insert into A values (?,?)"],
    ])
    def test_normal(self, table, insert_tuple, is_isert_many, expected):
        assert SqlQuery.make_insert(
            table, insert_tuple, is_isert_many) == expected

    @pytest.mark.parametrize(["table", "insert_tuple", "is_isert_many", "expected"], [
        ["", [], False, ValueError],
        ["", None, True, ValueError],
        ["", ["B"], False, ValueError],
        ["A", [], True, ValueError],
        ["A", None, False, ValueError],
        [None, None, True, ValueError],
        [None, ["B"], False, ValueError],
        [None, [], True, ValueError],
    ])
    def test_exception(self, table, insert_tuple, is_isert_many, expected):
        with pytest.raises(expected):
            SqlQuery.make_insert(table, insert_tuple)


class Test_make_where:

    @pytest.mark.parametrize(["key", "value", "operation", "expected"], [
        ["key", "value", "=", "key = 'value'"],
        ["key key", "value", "!=", "[key key] != 'value'"],
        ["%key+key", 100, "<", "[%key+key] < 100"],
        ["key.key", "555", ">", "[key.key] > 555"],

        ["key", None, "!=", "key != NULL"],
    ])
    def test_normal(self, key, value, operation, expected):
        assert SqlQuery.make_where(key, value, operation) == expected

    @pytest.mark.parametrize(["key", "value", "operation", "expected"], [
        ["key", "value", None, ValueError],
        ["key", "value", "INVALID_VALUE", ValueError],
    ])
    def test_exception(self, key, value, operation, expected):
        with pytest.raises(expected):
            SqlQuery.make_where(key, value, operation)


class Test_make_where_in:

    @pytest.mark.parametrize(["key", "value", "expected"], [
        ["key", ["attr_a", "attr_b"], "key IN ('attr_a', 'attr_b')"],
    ])
    def test_normal(self, key, value, expected):
        assert SqlQuery.make_where_in(key, value) == expected

    @pytest.mark.parametrize(["key", "value", "expected"], [
        ["key", None, TypeError],
        ["key", 1, TypeError],
        [None, ["attr_a", "attr_b"], TypeError],
        [None, None, TypeError],
    ])
    def test_exception(self, key, value, expected):
        with pytest.raises(expected):
            SqlQuery.make_where_in(key, value)


class Test_make_where_not_in:

    @pytest.mark.parametrize(["key", "value", "expected"], [
        ["key", ["attr_a", "attr_b"], "key NOT IN ('attr_a', 'attr_b')"],
    ])
    def test_normal(self, key, value, expected):
        assert SqlQuery.make_where_not_in(key, value) == expected

    @pytest.mark.parametrize(["key", "value", "expected"], [
        ["key", None, TypeError],
        ["key", 1, TypeError],
        [None, ["attr_a", "attr_b"], TypeError],
        [None, None, TypeError],
    ])
    def test_exception(self, key, value, expected):
        with pytest.raises(expected):
            SqlQuery.make_where_not_in(key, value)


@pytest.fixture
def con(tmpdir):
    p = tmpdir.join("tmp.db")
    con = connect_sqlite_database(str(p), "w")

    con.create_table_with_data(
        table_name=TEST_TABLE_NAME,
        attribute_name_list=["attr_a", "attr_b"],
        data_matrix=[
            [1, 2],
            [3, 4],
        ])

    con.create_db_info_table(TEST_DB_NAME, TEST_DB_VERSION)

    return con


@pytest.fixture
def con_profile(tmpdir):
    class TestOptions(object):
        profile = True

    p = tmpdir.join("tmp_profile.db")
    con = connect_sqlite_database(str(p), "w", TestOptions())

    con.create_table_with_data(
        table_name=TEST_TABLE_NAME,
        attribute_name_list=["attr_a", "attr_b"],
        data_matrix=[
            [1, 2],
            [3, 4],
        ])

    con.create_db_info_table(TEST_DB_NAME, TEST_DB_VERSION)

    return con


@pytest.fixture
def con_null():
    return SqliteWrapper()


class Test_SqliteWrapper_is_connected:

    def test_normal(self, con):
        assert con.is_connected()

    def test_null(self, con_null):
        assert not con_null.is_connected()


class Test_SqliteWrapper_check_connection:

    def test_normal(self, con):
        con.check_connection()

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.check_connection()


class Test_SqliteWrapper_check_database_name:

    def test_normal(self, con):
        con.check_database_name(TEST_DB_NAME)

    @pytest.mark.parametrize(["value", "expected"], [
        ["hoge", MissmatchError],
        [None, MissmatchError],
    ])
    def test_exception(self, con, value, expected):
        with pytest.raises(expected):
            con.check_database_name(value)

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.check_database_name("hoge")


class Test_SqliteWrapper_check_database_version:

    def test_normal(self, con):
        con.check_database_version(TEST_DB_VERSION)

    @pytest.mark.parametrize(["value", "expected"], [
        ["hoge", ValueError],
        [None, AttributeError],
        ["99.99.99", MissmatchError],
    ])
    def test_exception(self, con, value, expected):
        with pytest.raises(expected):
            con.check_database_version(value)

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.check_database_version("hoge")


class Test_SqliteWrapper_get_total_changes:

    def test_smoke(self, con):
        con.get_total_changes()

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.get_total_changes()


class Test_SqliteWrapper_connect:

    @pytest.mark.parametrize(["value", "mode", "expected"], [
        [None, "r", gfile.NullPathError],
        [nan, "r", gfile.NullPathError],
        ["", "r", gfile.NullPathError],
        ["/not/existing/file/__path__", "r", gfile.FileNotFoundError],

        [None, "w", gfile.NullPathError],
        [inf, "w", gfile.NullPathError],
        ["", "w", gfile.NullPathError],

        [None, "a", gfile.NullPathError],
        [1, "a", gfile.NullPathError],
        ["", "a", gfile.NullPathError],

        ["empty_file.txt", None, TypeError],
        ["empty_file.txt", inf, TypeError],
        ["empty_file.txt", "", ValueError],
        ["empty_file.txt", "invalid_mode", ValueError],
    ])
    def test_exception(self, value, mode, expected):
        con = SqliteWrapper()
        with pytest.raises(expected):
            con.connect(value, mode)


class Test_SqliteWrapper_execute_select:

    def test_smoke(self, con):
        result = con.execute_select(select="*", table=TEST_TABLE_NAME)
        assert result is not None

    @pytest.mark.parametrize(["attr", "table_name", "expected"], [
        ["not_exist_attr", TEST_TABLE_NAME, sqlite3.OperationalError],
        ["", TEST_TABLE_NAME, sqlite3.OperationalError],
        [None, TEST_TABLE_NAME, TypeError],
        ["attr_a", "not_exist_table", sqlite3.OperationalError],
        ["attr_a", "", ValueError],
        ["attr_a", None, ValueError],
    ])
    def test_exception(self, con, attr, table_name, expected):
        with pytest.raises(expected):
            con.execute_select(select=attr, table=table_name)

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.execute_select(select="*", table=TEST_TABLE_NAME)


class Test_SqliteWrapper_execute_insert:

    def test_smoke(self, con):
        assert con.execute_insert(
            TEST_TABLE_NAME, insert_record=[5, 6])

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.execute_insert(
                TEST_TABLE_NAME, insert_record=[5, 6])


class Test_SqliteWrapper_execute_insert_many:

    @pytest.mark.parametrize(["table_name", "value", "expected"], [
        [
            TEST_TABLE_NAME,
            [
                [7, 8],
                [9, 10],
            ],
            True,
        ],
        [
            TEST_TABLE_NAME,
            [
            ],
            True,
        ],
    ])
    def test_normal(self, con, table_name, value, expected):
        assert con.execute_insert_many(
            TEST_TABLE_NAME, value) == expected

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.execute_insert_many(
                TEST_TABLE_NAME, [])


class Test_SqliteWrapper_get_table_name_list:

    def test_normal(self, con):
        expected = set([
            SqliteWrapper.TN_TABLE_CONFIG, SqliteWrapper.TN_DB_INFO, TEST_TABLE_NAME
        ])

        assert set(con.get_table_name_list()) == expected

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.get_table_name_list()


class Test_SqliteWrapper_get_attribute_name_list:

    @pytest.mark.parametrize(["value", "expected"], [
        [
            TEST_TABLE_NAME,
            ["attr_a", "attr_b"],
        ],
    ])
    def test_normal(self, con,  value, expected):
        assert con.get_attribute_name_list(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        ["not_exist_table", TableNotFoundError],
        [None, TableNotFoundError],
    ])
    def test_null(self, con, value, expected):
        with pytest.raises(expected):
            con.get_attribute_name_list(value)

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.get_attribute_name_list("not_exist_table")


class Test_SqliteWrapper_get_attribute_type_list:

    @pytest.mark.parametrize(["value", "expected"], [
        [
            TEST_TABLE_NAME,
            ("integer", "integer"),
        ],
    ])
    def test_normal(self, con,  value, expected):
        assert con.get_attribute_type_list(value) == expected

    @pytest.mark.parametrize(["value", "expected"], [
        ["not_exist_table", TableNotFoundError],
        [None, TableNotFoundError],
    ])
    def test_null(self, con, value, expected):
        with pytest.raises(expected):
            con.get_attribute_type_list(value)

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.get_attribute_type_list(TEST_TABLE_NAME)


class Test_SqliteWrapper_has_table:

    @pytest.mark.parametrize(["value", "expected"], [
        [TEST_TABLE_NAME, True],
        ["not_exist_table", False],
        ["", False],
        [None, False],
    ])
    def test_normal(self, con, value, expected):
        assert con.has_table(value) == expected

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.has_table(TEST_TABLE_NAME)


class Test_SqliteWrapper_has_attribute:

    @pytest.mark.parametrize(["table", "attr", "expected"], [
        [TEST_TABLE_NAME, "attr_a", True],
        [TEST_TABLE_NAME, "not_exist_attr", False],
        [TEST_TABLE_NAME, "", False],
        [TEST_TABLE_NAME, None, False],
    ])
    def test_normal(self, con, table, attr, expected):
        assert con.has_attribute(table, attr) == expected

    @pytest.mark.parametrize(["value", "attr", "expected"], [
        ["not_exist_table", "attr_a", TableNotFoundError],
        [None, "attr_a", TableNotFoundError],
    ])
    def test_exception(self, con, value, attr, expected):
        with pytest.raises(expected):
            con.has_attribute(value, attr)

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.has_attribute(TEST_TABLE_NAME, "attr")


class Test_SqliteWrapper_has_attribute_list:

    @pytest.mark.parametrize(["table", "attr", "expected"], [
        [TEST_TABLE_NAME, ["attr_a"], True],
        [TEST_TABLE_NAME, ["attr_a", "attr_b"], True],
        [TEST_TABLE_NAME, ["attr_a", "attr_b", "not_exist_attr"], False],
        [TEST_TABLE_NAME, ["not_exist_attr"], False],
        [TEST_TABLE_NAME, [], False],
        [TEST_TABLE_NAME, None, False],
    ])
    def test_normal(self, con, table, attr, expected):
        assert con.has_attribute_list(table, attr) == expected

    @pytest.mark.parametrize(["value", "attr", "expected"], [
        ["not_exist_table", ["attr_a"], TableNotFoundError],
        [None, ["attr_a"], TableNotFoundError],
    ])
    def test_exception(self, con, value, attr, expected):
        with pytest.raises(expected):
            con.has_attribute_list(value, attr)

    def test_null(self, con_null):
        with pytest.raises(NullDatabaseConnectionError):
            con_null.has_attribute_list(TEST_TABLE_NAME, "attr")


class Test_SqliteWrapper_get_profile:

    def test_normal(self, con):
        attribute_name_list, profile_list = con.get_profile()
        assert is_empty_list_or_tuple(attribute_name_list)
        assert is_empty_list_or_tuple(profile_list)

    def test_normal_profile(self, con_profile):
        attribute_name_list, profile_list = con_profile.get_profile()
        assert is_not_empty_list_or_tuple(attribute_name_list)
        assert is_not_empty_list_or_tuple(profile_list)


class Test_SqliteWrapper_verify_table_existence:

    def test_normal(self, con):
        con.verify_table_existence(TEST_TABLE_NAME)

    def test_exception(self, con):
        with pytest.raises(TableNotFoundError):
            con.verify_table_existence("not_exist_table")


class Test_SqliteWrapper_verify_attribute_existence:

    @pytest.mark.parametrize(["table", "attr", "expected"], [
        [TEST_TABLE_NAME, "not_exist_attr", AttributeNotFoundError],
        ["not_exist_table", "attr_a", TableNotFoundError],
        [None, "attr_a", ValueError],
        ["", "attr_a", ValueError],
    ])
    def test_normal(self, con, table, attr, expected):
        with pytest.raises(expected):
            con.verify_attribute_existence(table, attr)


class Test_SqliteWrapper_drop_table:

    def test_normal(self, con):
        attr_description_list = [
            "'%s' %s" % ("attr_name", "TEXT")
        ]

        table_name = "new_table"

        assert not con.has_table(table_name)

        con.create_table(table_name, attr_description_list)
        assert con.has_table(table_name)

        con.drop_table(table_name)
        assert not con.has_table(table_name)


class Test_SqliteWrapper_rollback:

    def test_normal(self, con):
        assert con.rollback()

    def test_null(self, con_null):
        assert con_null.rollback()


class Test_SqliteWrapper_commit:

    def test_normal(self, con):
        assert con.commit()

    def test_null(self, con_null):
        assert con_null.commit()


class Test_SqliteWrapper_close:

    def test_close(self, con):
        assert con.close()

    def test_null(self, con_null):
        assert con_null.close()


class Test_connect_sqlite_db_mem:

    def test_normal(self):
        assert connect_sqlite_db_mem() is not None


class Test_connect_sqlite_database:

    @pytest.mark.parametrize(["db_path", "mode"], [
        ["tmp.db", "w"],
        ["tmp.db", "a"],
    ])
    def test_normal(self, tmpdir, db_path, mode):
        p = str(tmpdir.join(db_path))
        assert connect_sqlite_database(p, mode) is not None
        assert connect_sqlite_database(p, "r") is not None
