# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

import logging
import os
import re
import sys
import sqlite3

import six
from six.moves import range
from six.moves import map

import thutils
import thutils.common as common
import thutils.gfile as gfile
import thutils.gtime as gtime
from thutils.logger import logger


DB_DATETIME_FORMAT = "%Y%m%d%H%M%S"
SQLITE_EXTENSION = ".sqlite"

MEMORY_DB_NAME = ":memory:"


class SqlQuery:
    __RE_SANITIZE = re.compile("[%s]" % (re.escape("%/()[]<>.:;'!\# -+=\n")))
    __RE_TABLE_STR = re.compile("[%s]" % (re.escape("%()-+/.")))
    __RE_TO_ATTR_STR = re.compile("[%s0-9\s#]" % (re.escape("[%()-+/.]")))

    __VALID_WHERE_OPERATION_LIST = [
        "=", "==", "!=", "<>", ">", ">=", "<", "<="]

    @classmethod
    def sanitize(cls, query_item):
        return cls.__RE_SANITIZE.sub("", query_item)

    @classmethod
    def to_table_str(cls, name):
        if cls.__RE_TABLE_STR.search(name):
            return "[%s]" % (name)

        if common.RE_SPACE.search(name):
            return "'%s'" % (name)

        return name

    @classmethod
    def to_attr_str(cls, name, operation_query=""):
        if cls.__RE_TO_ATTR_STR.search(name):
            sql_name = "[%s]" % (name)
        elif name == "join":
            sql_name = "[%s]" % (name)
        else:
            sql_name = name

        if common.is_not_empty_string(operation_query):
            sql_name = "%s(%s)" % (operation_query, sql_name)

        return sql_name

    @classmethod
    def to_attr_str_list(cls, name_list, operation_query=None):
        if common.is_empty_string(operation_query):
            return map(cls.to_attr_str, name_list)

        return [
            "%s(%s)" % (operation_query, cls.to_attr_str(name))
            for name in name_list
        ]

    @classmethod
    def to_value_str(cls, value):
        if value is None:
            return "NULL"

        if common.is_integer(value) or common.is_float(value):
            return str(value)

        return "'%s'" % (value)

    @classmethod
    def to_value_str_list(cls, value_list):
        return map(cls.to_value_str, value_list)

    @classmethod
    def make_select(cls, select, table, where=None, extra=None):
        """
        SQLite query作成補助関数
        SQLiteWrapper classのメソッドからのみ呼ばれる

        Return value: SQLite query string
        """

        """
        if common.is_empty_string(select):
            raise ValueError("empty select query")

        if common.is_empty_string(table):
            logger.error("empty table name")
            return ""
        """

        query_list = [
            "SELECT " + select,
            "FROM " + SqlQuery.to_table_str(table),
        ]
        if common.is_not_empty_string(where):
            query_list.append("WHERE " + where)
        if common.is_not_empty_string(extra):
            query_list.append(extra)

        return " ".join(query_list)

    @classmethod
    def make_insert(cls, table_name, insert_tuple, is_insert_many=False):
        table_name = SqlQuery.to_table_str(table_name)
        if common.is_empty_string(table_name):
            raise ValueError("table name is empty")

        if common.is_empty_list_or_tuple(insert_tuple):
            raise ValueError("empty insert list/tuple")

        if is_insert_many:
            value_list = ['?' for _i in insert_tuple]
        else:
            value_list = [str(value) for value in insert_tuple]

        return "insert into %s values (%s)" % (
            table_name, ",".join(value_list))

    @classmethod
    def make_where(cls, key, value, operation="="):
        if operation not in cls.__VALID_WHERE_OPERATION_LIST:
            raise ValueError("operation not supported: " + str(operation))

        # if value is None:
        #    value = "NULL"

        return "%s %s %s" % (
            cls.to_attr_str(key), operation, cls.to_value_str(value))

    @classmethod
    def make_where_in(cls, key, value_list):
        return "%s IN (%s)" % (
            cls.to_attr_str(key), ", ".join(cls.to_value_str_list(value_list)))

    @classmethod
    def make_where_not_in(cls, key, value_list):
        return "%s NOT IN (%s)" % (
            cls.to_attr_str(key), ", ".join(cls.to_value_str_list(value_list)))

    @classmethod
    def make_datetimerange_where_list(
            cls, datetime_range, start_attr_name, end_attr_name):
        import copy

        if datetime_range is None:
            return []

        where_query_list = []
        dtr_work = copy.copy(datetime_range)
        dtr_work.time_format = DB_DATETIME_FORMAT

        if gtime.is_datetime(dtr_work.start_datetime):
            where_query = cls.make_where(
                start_attr_name,
                dtr_work.getStartTimeText(),
                operation=">=")
            where_query_list.append(where_query)

        if gtime.is_datetime(datetime_range.end_datetime):
            where_query = cls.make_where(
                end_attr_name,
                dtr_work.getEndTimeText(),
                operation="<=")
            where_query_list.append(where_query)

        return where_query_list


def getListFromQueryResult(result):
    """
    :argument:
        Return value from a SQLite query response

    :return value:
        list
    """

    return [record[0] for record in result]

    """
    result_list = []
    for column_idx in result:
        result_list.append(column_idx[0])
    return result_list
    """


def copyTable(con_src, con_dst, table_name):
    if con_src is None:
        logger.error("null source database")
        return False

    if con_dst is None:
        logger.error("null destination database")
        return False

    if not con_src.has_table(table_name):
        logger.warn(
            "not found '%s' table in %s" % (table_name, con_src.database_path))
        return False

    logger.debug("copy '%s' table: %s to %s" % (
        table_name, con_src.database_path, con_dst.database_path))

    result = con_src.execute_select(select="*", table=table_name)
    if result is None:
        return False

    value_matrix = result.fetchall()

    return con_dst.create_table_with_data(
        table_name,
        con_src.getAttributeNameList(table_name),
        value_matrix)


def appendTable(con_src, con_dst, table_name):
    logger.debug("append '%s' table: %s -> %s" % (
        table_name, con_src.database_path, con_dst.database_path))

    result = con_src.execute_select(select="*", table=table_name)
    if result is None:
        return False

    value_matrix = []
    for value_list in result.fetchall():
        value_matrix.append(value_list)

    if not con_dst.has_table(table_name):
        con_dst.create_table_with_data(
            table_name, con_src.getAttributeNameList(table_name),
            value_matrix)
    else:
        con_dst.execute_insert_many(table_name, value_matrix)

    return True


# class ---


class DatabaseError(Exception):
    pass


class NullDatabaseConnectionError(Exception):
    pass


class TableNotFoundError(Exception):
    pass


class AttributeNotFoundError(Exception):
    pass


class MissmatchError(Exception):
    pass


class SqliteWrapper(object):
    '''
    wrapper class of sqlite3
    '''

    # Table Nmae
    TN_DB_INFO = "database_information"
    TN_TABLE_CONFIG = "table_configuration"
    TN_SQL_PROFILE = "sql_profile"

    MISC_TABLE_LIST = [
        TN_TABLE_CONFIG,
        TN_DB_INFO,
        TN_SQL_PROFILE,
    ]

    # Attribute Name
    AN_DB_NAME = "database_name"
    AN_DB_VERSION = "database_version"
    AN_DB_CREATE_TIME = "database_create_time"

    @property
    def database_path(self):
        return self.__database_path

    @property
    def connection(self):
        return self.__connection

    @property
    def mode(self):
        return self.__mode

    @property
    def dry_run(self):
        return self.__dry_run

    def __init__(self, dry_run=False, profile=False):
        self.cursur = None
        self.auto_commit = True
        self.sql_debug = False
        self.is_logging_query = False

        self.__dry_run = dry_run
        self.__database_path = None
        self.__connection = None
        self.__mode = None

        self.__is_profile = profile
        self.__dict_query_count = {}
        self.__dict_query_totalexectime = {}

    def __del__(self):
        self.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def is_connected(self):
        if self.dry_run:
            return True

        try:
            self.check_connection()
        except NullDatabaseConnectionError:
            return False

        return True

    def check_connection(self):
        """
        raise NullDatabaseConnectionError
        if not connected to a SQLite database file
        """

        if self.dry_run:
            return

        if self.connection is None:
            raise NullDatabaseConnectionError("null database connection")

        if common.is_empty_string(self.database_path):
            raise NullDatabaseConnectionError("null database file path")

    def check_database_name(self, expected_name):
        """
        raise:
            TableNotFoundError: table not found in the database
            AttributeError: attribute not found in the database
            MissmatchError: database name missmatch found
        """

        table_name = self.TN_DB_INFO

        self.check_connection()
        self.verify_table_existence(table_name)

        database_name = self.getDatabaseName()
        if common.is_empty_string(database_name):
            message = "'%s' attribute not found in '%s' table" % (
                self.AN_DB_NAME, table_name)
            raise AttributeError(message)

        if database_name != expected_name:
            dict_msg = {
                "name": database_name,
                "expected": expected_name,
                "database": self.database_path,
            }
            message = "mismatch database name: " + common.dump_dict(dict_msg)

            raise MissmatchError(message)

        logger.debug("valid database name: %s" % (self.TN_DB_INFO))

    def check_database_version(self, compare_version):
        """
        raise:
                TableNotFoundError: table not found in the database
                AttributeError: attribute not found in the database
                MissmatchError: database version missmatch found
        """

        self.check_connection()

        database_version = self.getDatabaseVersion()
        if common.is_empty_string(database_version):
            message = "%s attribute not found in %s table" % (
                self.AN_DB_VERSION, self.TN_DB_INFO)
            raise AttributeError(message)

        if common.compare_version(database_version, compare_version) != 0:
            message = "mismatch database version: %s and %s" % (
                database_version, compare_version)
            raise MissmatchError(message)

        logger.debug(
            "valid %s version: %s" % (self.TN_DB_INFO, database_version))

    def checkAccessPermission(self, valid_permission_list):
        if self.mode is None:
            return

        if self.mode not in valid_permission_list:
            raise thutils.PermissionError(str(valid_permission_list))

    def connect(self, database_path, mode="w"):
        """
        mode:
                "r": read only
                "w": DBファイルを新規作成する。既存ファイルは削除する。
                "a": 既存DBファイルに追記する。

        raise:
                TypeError:
                        - database_path が文字列でない
                        - mode が文字列でない
                FileNotFoundError:
                        - database_path がない
                InvalidFilePathError:
                        - database_path が有効なパスでない
                ValueError:
                        - database_path がディレクトリ
                        - mode が未サポートの値
                DatabaseError:
                        - SQLiteデータベースバイナリファイルでない

        Return value:
                nothing
        """

        gfile.validate_path(database_path)
        self.close()

        if mode == "r":
            self.__verify_sqlite_db_file(database_path)
        elif mode in ["w", "a"]:
            if database_path != MEMORY_DB_NAME:
                try:
                    gfile.check_file_existence(database_path)
                except gfile.FileNotFoundError:
                    pass

                if mode == "w":
                    gfile.FileManager.remove_file(database_path)
        else:
            raise ValueError("unknown connection mode: " + mode)

        self.__database_path = os.path.realpath(database_path)
        logger.debug("connect to " + database_path)

        if self.dry_run:
            return

        self.__connection = sqlite3.connect(
            database_path,
            #detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            cached_statements=256)
        self.__mode = mode
        #self.__connection.row_factory	= sqlite3.Row

        #sqlite3.dbapi2.converters['DATETIME']	= sqlite3.dbapi2.converters['TIMESTAMP']

    def execute_select(self, select, table, where=None, extra=None):
        query = SqlQuery.make_select(select, table, where, extra)
        if self.sql_debug:
            logger.debug(query)
        result = self.__execute(query, logging.getLogger().findCaller())
        if result is None:
            message = "null result: query='%s', db=%s" % (
                query, self.database_path)
            logger.debug(message)
            return None

        return result

    def execute_insert(self, table_name, insert_record):
        self.checkAccessPermission(["w", "a"])

        query = SqlQuery.make_insert(
            table_name, insert_record)
        self.__logging("execute query: %s %s" % (query, insert_record))

        if self.dry_run:
            return True

        self.__execute(query, logging.getLogger().findCaller())

        return True

    def execute_insert_many(self, table_name, insert_record_list):
        self.checkAccessPermission(["w", "a"])

        logger.debug("insert %d records to '%s'" % (
            len(insert_record_list), table_name))

        self.verify_table_existence(table_name)

        if common.is_empty_list_or_tuple(insert_record_list):
            logger.debug("empty record list")
            return True

        query = SqlQuery.make_insert(
            table_name, insert_record_list[0], is_insert_many=True)
        self.__logging("insert many record: query=%s, size=%d, db=%s" % (
            query, len(insert_record_list), self.database_path))

        if self.dry_run:
            return True

        try:
            self.connection.executemany(query, insert_record_list)
            return True
        except Exception:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            caller = logging.getLogger().findCaller()
            file_path, line_no, func_name = caller[:3]
            logger.error(
                "%s(%d) %s: failed to execute query:\n" % (
                    file_path, line_no, func_name) +
                "  query=%s\n" % (query) +
                "  msg='%s'\n" % (str(e)) +
                "  db=%s\n" % (self.database_path) +
                "  records=%s\n" % (insert_record_list[:2])
            )

            return False

    def get_total_changes(self):
        if self.dry_run:
            return 0

        self.check_connection()

        return self.connection.total_changes

    def getValue(self, select, table, where=None, extra=None):
        query = SqlQuery.make_select(select, table, where, extra)
        result = self.__execute(query, logging.getLogger().findCaller())
        if result is None:
            return None

        return common.getListItem(result.fetchone(), 0)

    def getValueList(self, select, table, where=None, extra=None):
        query = SqlQuery.make_select(select, table, where, extra)
        result = self.__execute(query, caller=logging.getLogger().findCaller())
        if result is None:
            return []

        return getListFromQueryResult(result.fetchall())

    def getDatabaseName(self):
        table_name = self.TN_DB_INFO
        self.verify_table_existence(table_name)

        return self.getValue(
            select=common.AN_GeneralValue,
            table=table_name,
            where=SqlQuery.make_where(common.AN_GeneralKey, self.AN_DB_NAME))

    def getDatabaseVersion(self):
        table_name = self.TN_DB_INFO
        self.verify_table_existence(table_name)

        return self.getValue(
            select=common.AN_GeneralValue,
            table=table_name,
            where=SqlQuery.make_where(common.AN_GeneralKey, self.AN_DB_VERSION))

    def get_table_name_list(self):
        try:
            self.check_connection()
        except NullDatabaseConnectionError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return []

        query = "SELECT name FROM sqlite_master WHERE TYPE='table'"
        result = self.__execute(query, logging.getLogger().findCaller())
        if result is None:
            return []

        return getListFromQueryResult(result.fetchall())

    def getAttributeNameList(self, table_name):
        if not self.has_table(table_name):
            logger.warn("'%s' table not found in %s" % (
                table_name, self.database_path))
            return []

        query = "SELECT * FROM '%s'" % (table_name)
        result = self.__execute(query, logging.getLogger().findCaller())
        return getListFromQueryResult(result.description)

    def getFieldNameTypeList(self, table_name):
        if not self.has_table(table_name):
            logger.warn("'%s' table not found in %s" % (
                table_name, self.database_path))
            return []

        attribute_name_list = self.getAttributeNameList(table_name)
        query = "SELECT DISTINCT %s FROM '%s'" % (
                ",".join([
                    "TYPEOF(%s)" % (SqlQuery.to_attr_str(attribute))
                    for attribute in attribute_name_list]),
                table_name)
        result = self.__execute(query, logging.getLogger().findCaller())

        return getListFromQueryResult(result.fetchall())

    def rollback(self):
        try:
            self.check_connection()
        except NullDatabaseConnectionError:
            return True

        logger.info("rollback %s" % (self.database_path))
        self.connection.rollback()

        return True

    def commit(self):
        if self.dry_run:
            return True

        try:
            self.check_connection()
        except NullDatabaseConnectionError:
            return True

        logger.debug("commit to %s" % (self.database_path))
        self.connection.commit()

        return True

    def get_profile(self, get_profile_count=50):
        con_tmp = connect_sqlite_db_mem()

        value_matrix = []
        for query, execute_time in six.iteritems(self.__dict_query_totalexectime):
            call_count = self.__dict_query_count.get(query, 0)
            value_list = [query, execute_time, call_count]
            value_matrix.append(value_list)

        attribute_name_list = ["query", "execution_time", "count"]
        con_tmp.create_table_with_data(
            self.TN_SQL_PROFILE,
            attribute_name_list,
            data_matrix=value_matrix)
        con_tmp.commit()

        result = con_tmp.execute_select(
            select="%s,SUM(%s),SUM(%s)" % (
                "query", "execution_time", "count"),
            table=self.TN_SQL_PROFILE,
            extra="GROUP BY %s ORDER BY %s DESC LIMIT %d" % (
                "query", "execution_time", get_profile_count))
        if result is None:
            return [], []

        return attribute_name_list, result.fetchall()

    def close(self):
        if self.dry_run:
            return True

        try:
            self.check_connection()
        except NullDatabaseConnectionError:
            return True

        self.commit()
        logger.debug("close database: path=%s, changes=%d" % (
            self.database_path, self.get_total_changes()))

        self.connection.close()
        self.__init__()

        return True

    def has_table(self, table_name):
        if self.dry_run:
            return True

        if common.is_empty_string(table_name):
            return False

        return table_name in self.get_table_name_list()

    def has_attribute(self, table_name, attribute_name):
        return attribute_name in self.getAttributeNameList(table_name)

    def hasAttributeList(self, table_name, attribute_name_list):
        not_exist_field_list = []
        for attribute_name in attribute_name_list:
            if not self.has_attribute(table_name, attribute_name):
                not_exist_field_list.append(attribute_name)

        if len(not_exist_field_list) > 0:
            logger.warn(
                "attribute not exists: %s" % (", ".join(not_exist_field_list)))
            return False

        return True

    def verify_table_existence(self, table_name):
        """
        raise:
                TypeError
                TableNotFoundError
        """

        if common.is_empty_string(table_name):
            raise TypeError("null string")

        found_table = self.has_table(table_name)

        if found_table:
            msg_format = "'%s' table found in %s"
        else:
            msg_format = "'%s' table not found %s"

        message = msg_format % (table_name, self.database_path)

        if found_table:
            logger.debug(message)
        else:
            raise TableNotFoundError(message)

    def verify_attribute_existence(self, table_name, attribute_name):
        """
        raise:
                TypeError
                TableNotFoundError
                AttributeNotFoundError
        """

        self.verify_table_existence(table_name)

        found_attr = self.has_attribute(table_name, attribute_name)

        if found_attr:
            msg_format = "'%s' attribute found in '%s' table"
        else:
            msg_format = "'%s' attribute not found in '%s' table"
        message = msg_format % (attribute_name, table_name)

        if found_attr:
            logger.debug(message)
        else:
            raise AttributeNotFoundError(message)

    def drop_table(self, table_name, is_drop_existing_table=True):
        self.checkAccessPermission(["w", "a"])

        if self.has_table(table_name) and is_drop_existing_table:
            logger.debug("drop table: " + table_name)

            query = "DROP TABLE IF EXISTS '%s'" % (table_name)
            self.__execute(query, logging.getLogger().findCaller())
            self.commit()

    def create_table(self, table_name, attribute_description_list):
        self.checkAccessPermission(["w", "a"])

        table_name = table_name.strip()
        if self.has_table(table_name):
            logger.debug("table already exists: " + table_name)
            return True

        query = "CREATE TABLE IF NOT EXISTS '%s' (%s)" % (
                table_name, ", ".join(attribute_description_list))
        if self.__execute(query, logging.getLogger().findCaller()) is None:
            if not self.dry_run:
                return False

        return True

    def createIndex(self, table_name, attribute_name):
        self.checkAccessPermission(["w", "a"])

        index_name = "%s_%s_index" % (
            SqlQuery.sanitize(table_name), SqlQuery.sanitize(attribute_name))
        logger.debug(
            "create index: table='%s, attribute='%s', index_name=%s" % (
                table_name, attribute_name, index_name))
        query = "CREATE INDEX IF NOT EXISTS %s ON %s('%s')" % (
                index_name, SqlQuery.to_table_str(table_name), attribute_name)
        self.__execute(query, logging.getLogger().findCaller())

    def createIndexList(self, table_name, attribute_name_list):
        self.checkAccessPermission(["w", "a"])

        if common.is_empty_list_or_tuple(attribute_name_list):
            return

        for attribute in attribute_name_list:
            self.createIndex(table_name, attribute)

    def create_table_with_data(
            self, table_name, attribute_name_list, data_matrix,
            index_attribute_list=()):

        self.checkAccessPermission(["w", "a"])

        strip_index_attribute_list = list(
            set(attribute_name_list).intersection(set(index_attribute_list)))

        if common.is_empty_list_or_tuple(data_matrix):
            msg = "null input data: '%s (%s)'" % (
                table_name, ", ".join(attribute_name_list))
            logger.warn(msg)
            return True

        self.__verify_value_matrix(attribute_name_list, data_matrix)

        attr_description_list = []
        table_config_matrix = []
        for col, value_type in sorted(
                six.iteritems(self.__get_column_valuetype(data_matrix))):
            attr_name = attribute_name_list[col]
            attr_description_list.append(
                "'%s' %s" % (attr_name, value_type))

            table_config_matrix.append([
                table_name,
                attr_name,
                value_type,
                True if attr_name in strip_index_attribute_list else False,
            ])

        self.__create_table_config(table_config_matrix)
        self.create_table(table_name, attr_description_list)

        if not self.execute_insert_many(table_name, data_matrix):
            raise DatabaseError("failed to insert record to " + table_name)

        self.createIndexList(table_name, strip_index_attribute_list)
        self.__auto_commit()

        return True

    def create_db_info_table(self, db_name, db_version):
        import datetime
        import thutils.environment

        self.checkAccessPermission(["w", "a"])

        table_name = self.TN_DB_INFO
        if self.has_table(table_name):
            logger.debug("'%s' table already exists" % (table_name))
            return True

        value_matrix = [
            [self.AN_DB_NAME, db_name],
            [self.AN_DB_VERSION, db_version],
            [
                self.AN_DB_CREATE_TIME,
                datetime.datetime.now().strftime(DB_DATETIME_FORMAT)
            ],
        ]
        value_matrix.extend(
            thutils.environment.EnvironmentInfo.getGeneralInfoMatrix())

        return self.create_table_with_data(
            table_name, common.KEY_VALUE_HEADER, value_matrix)

    def __auto_commit(self):
        if self.auto_commit:
            self.commit()

    @staticmethod
    def __verify_sqlite_db_file(database_path):
        if gfile.check_file_existence(database_path) == gfile.FileType.DIRECTORY:
            raise ValueError(
                "%s is not a database file, but a directory." % (
                    database_path))

        connection = sqlite3.connect(database_path)
        try:
            connection.execute(
                "SELECT name FROM sqlite_master WHERE TYPE='table'")
        except:
            message = "invalid SQLite database: " + database_path
            raise DatabaseError(message)

    @staticmethod
    def __verify_value_matrix(field_list, value_matrix):
        miss_match_idx_list = []

        for list_idx in range(len(value_matrix)):
            if len(field_list) == len(value_matrix[list_idx]):
                continue

            miss_match_idx_list.append(list_idx)

        if len(miss_match_idx_list) == 0:
            return

        sample_miss_match_list = value_matrix[miss_match_idx_list[0]]

        raise ValueError(
            "miss match header length and value length:" +
            "  header: %d %s\n" % (len(field_list), str(field_list)) +
            "  # of miss match line: %d ouf of %d\n" % (
                len(miss_match_idx_list), len(value_matrix)) +
            "  e.g. value at %d: %d %s\n" % (
                miss_match_idx_list[0],
                len(sample_miss_match_list), str(sample_miss_match_list))
        )

    @staticmethod
    def __get_value_type(value):
        if common.is_integer(value):
            return "INTEGER"

        if common.is_float(value):
            return "REAL"

        if gtime.is_datetime(value):
            return "DATETIME"

        return "TEXT"

    def __get_column_valuetype(self, value_matrix):
        """
        get value type of column

        return:
                { column_number : value_type }
        """

        dict_column_valuetype = {}
        for col, _ in enumerate(value_matrix[0]):
            dict_column_valuetype[col] = "INTEGER"

        col = 0
        for col_value_list in zip(*value_matrix):
            for cursor_value in col_value_list:
                cursor_value_type = self.__get_value_type(cursor_value)
                if all([
                    cursor_value is not None,
                    dict_column_valuetype[col] == "INTEGER",
                    cursor_value_type == "INTEGER"
                ]):
                    continue

                dict_column_valuetype[col] = cursor_value_type
                if cursor_value_type == "TEXT":
                    break

            col += 1

        return dict_column_valuetype

    def __logging(self, message):
        if not self.is_logging_query:
            return

        logger.debug(self, message)

    def __execute(self, query, caller=None):
        import time

        if caller is None:
            message = "execute query: " + query
        else:
            file_path, line_no, func_name = caller[:3]
            message = "execute query from %s(%d) %s: %s" % (
                os.path.basename(os.path.realpath(file_path)),
                line_no, func_name, query)
        message += " (%s)" % (self.database_path)
        self.__logging(message)

        if self.dry_run:
            return None

        self.check_connection()
        if common.is_empty_string(query):
            return None

        if self.__is_profile:
            exec_start_time = time.time()

        try:
            result = self.connection.execute(query)
        except Exception:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            if caller is None:
                caller = logging.getLogger().findCaller()
            file_path, line_no, func_name = caller[:3]
            message_list = [
                "failed to execute query at %s(%d) %s" % (
                    file_path, line_no, func_name),
                "  - query: %s" % (query),
                "  - msg:   %s" % (e),
                "  - db:    %s" % (self.database_path),
            ]
            logger.exception(e, os.linesep.join(message_list))
            # return None
            raise e

        if self.__is_profile:
            self.__dict_query_count[
                query] = self.__dict_query_count.get(query, 0) + 1

            elapse_time = time.time() - exec_start_time
            self.__dict_query_totalexectime[query] = (
                self.__dict_query_totalexectime.get(query, 0) + elapse_time)

        return result

    def __create_table_config(self, table_config_matrix):
        table_config_attr_list = [
            "table name", "attribute name", "value type", "create index"]

        attr_description_list = []
        for attr_name in table_config_attr_list:
            attr_description_list.append("'%s' %s" % (attr_name, "TEXT"))

        table_name = self.TN_TABLE_CONFIG
        if not self.has_table(table_name):
            self.create_table(table_name, attr_description_list)

        self.execute_insert_many(table_name, table_config_matrix)


def connect_sqlite_db_mem():
    con_mem = SqliteWrapper()
    con_mem.connect(MEMORY_DB_NAME)

    return con_mem


def connect_sqlite_database(db_path, mode, options=None):
    """
    SQLiteデータベースファイルへのコネクションを返す。
    """

    dry_run = False
    profile = False
    sql_logging = False

    if options is not None:
        dry_run = options.__dict__.get("dry_run", False)
        profile = options.__dict__.get("profile", False)
        sql_logging = options.__dict__.get("sql_logging", False)

    con = SqliteWrapper(dry_run, profile)
    con.is_logging_query = sql_logging
    con.connect(db_path, mode)

    return con
