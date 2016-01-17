'''
@author: Tsuyoshi Hombashi

:required:
    https://pypi.python.org/pypi/pytest
'''

import os

import pytest
from six.moves import range

from thutils.sqlite import *
import thutils.gfile as gfile


nan = float("nan")
inf = float("inf")


class Test_sanitize:
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
        ["a", 2, "a"],
        ["a", True, "a"],
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

    """
    @pytest.mark.parametrize(
        ["select", "table", "where", "extra", "expected"], [
            ["A", None, None, None, ""],
        ])
    def test_abnormal(self, select, table, where, extra, expected):
        assert SqlQuery.make_select(select, table, where, extra) == expected
    """

    @pytest.mark.parametrize(
        ["select", "table", "where", "extra", "expected"], [
            ["A", None, None, None, TypeError],
            [None, None, None, None, TypeError],
            [None, "B", None, None, TypeError],
            [nan, None, None, None, TypeError],
            [nan, nan, None, None, TypeError],
            [nan, nan, nan, None, TypeError],
            [nan, nan, nan, nan, TypeError],
        ])
    def test_exception(self, select, table, where, extra, expected):
        with pytest.raises(expected):
            SqlQuery.make_select(select, table, where, extra)


class Test_make_insert:

    @pytest.mark.parametrize(["table", "insert_tuple", "expected"], [
        ["A", ["B"], "insert into A values (?)"],
        ["A", ["B"] * 2, "insert into A values (?,?)"],
    ])
    def test_normal(self, table, insert_tuple, expected):
        assert SqlQuery.make_insert(table, insert_tuple) == expected

    @pytest.mark.parametrize(["table", "insert_tuple", "expected"], [
        ["A", [], ""],
        ["A", None, ""],
    ])
    def test_abnormal(self, table, insert_tuple, expected):
        assert SqlQuery.make_insert(table, insert_tuple) == expected

    @pytest.mark.parametrize(["table", "insert_tuple", "expected"], [
        ["", [], ValueError],
        ["", None, ValueError],
        ["", ["B"], ValueError],
        [None, None, TypeError],
        [None, ["B"], TypeError],
        [None, [], TypeError],
    ])
    def test_exception(self, table, insert_tuple, expected):
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


class Test_SqliteWrapper_abnormal:

    @pytest.fixture
    def con(self):
        return SqliteWrapper()

    def test_is_connected(self, con):
        assert not con.is_connected()

    def test_check_connection(self, con):
        with pytest.raises(NullDatabaseConnectionError):
            con.check_connection()

    def test_check_database_name(self, con):
        with pytest.raises(NullDatabaseConnectionError):
            con.check_database_name("hoge")

    def test_check_database_version(self, con):
        with pytest.raises(NullDatabaseConnectionError):
            con.check_database_version("hoge")

    def test_getTotalChanges(self, con):
        with pytest.raises(NullDatabaseConnectionError):
            con.getTotalChanges()

    @pytest.mark.parametrize(["value", "mode", "expected"], [
        [None, "r", gfile.InvalidFilePathError],
        [nan, "r", gfile.InvalidFilePathError],
        ["", "r", gfile.InvalidFilePathError],
        ["/not/existing/file/__path__", "r", gfile.FileNotFoundError],

        [None, "w", gfile.InvalidFilePathError],
        [inf, "w", gfile.InvalidFilePathError],
        ["", "w", gfile.InvalidFilePathError],

        [None, "a", gfile.InvalidFilePathError],
        [1, "a", gfile.InvalidFilePathError],
        ["", "a", gfile.InvalidFilePathError],

        ["empty_file.txt", None, TypeError],
        ["empty_file.txt", inf, TypeError],
        ["empty_file.txt", "", ValueError],
        ["empty_file.txt", "invalid_mode", ValueError],
    ])
    def test_connect(self, con, value, mode, expected):
        with pytest.raises(expected):
            con.connect(value, mode)

    def test_execute_select(self, con):
        with pytest.raises(NullDatabaseConnectionError):
            con.execute_select(select="*", table="table")

    def test_rollback(self, con):
        assert con.rollback()

    def test_commit(self, con):
        assert con.commit()

    def test_close(self, con):
        assert con.close()
