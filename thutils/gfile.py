# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

from __future__ import with_statement
import os.path
import re
import sys

import dataproperty
import path
import pathvalidate
import six

from thutils.logger import logger


class FileType:
    FILE = 1
    DIRECTORY = 2
    LINK = 3


class NullPathError(Exception):
    pass


class InvalidFilePathError(Exception):
    pass


class FileNotFoundError(Exception):
    pass


class EmptyFileError(Exception):
    pass


class FileTypeChecker:

    class FileType:
        TEXT = "ASCII text"
        BINARY = "data"

    __re_text = re.compile(FileType.TEXT)

    @classmethod
    def get_file_type(cls, file_path):
        import magic

        return magic.from_file(file_path)

    @classmethod
    def is_text_file(cls, file_path):
        try:
            file_type_text = cls.get_file_type(file_path).decode("utf-8")
        except UnicodeDecodeError:
            return False

        return cls.__re_text.search(file_type_text) is not None


class FileManager:
    __dry_run = False

    @classmethod
    def initialize(cls, dry_run):
        cls.__dry_run = dry_run

    @classmethod
    def touch(cls, touch_path):
        logger.debug("touch file: " + touch_path)

        if cls.__dry_run:
            return

        path_obj = path.Path(touch_path)
        cls.make_directory(path_obj.dirname())

        return path_obj.touch()

    @classmethod
    def make_directory(cls, dir_path, force=False):
        try:
            check_file_existence(dir_path)
        except FileNotFoundError:
            pass
        else:
            logger.debug("directory already exists: " + dir_path)
            return path.Path(dir_path)

        logger.debug("make directory: " + dir_path)
        path_obj = path.Path(dir_path)

        if any([not cls.__dry_run, force]):
            return path_obj.makedirs_p()

        return path_obj

    @classmethod
    def copy_file(cls, src_path, dst_path):
        import shutil

        try:
            check_file_existence(src_path)
        except FileNotFoundError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.debug(e)
            return False

        logger.debug("copy: %s -> %s" % (src_path, dst_path))
        if cls.__dry_run:
            return True

        try:
            shutil.copyfile(src_path, dst_path)
        except (shutil.Error, IOError):
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.debug("skip copy: " + str(e))

        return True

    @classmethod
    def moveFile(cls, src_path, dst_path):
        import shutil

        try:
            check_file_existence(src_path)
        except FileNotFoundError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.debug(e)
            return False

        if os.path.realpath(src_path) == os.path.realpath(dst_path):
            logger.debug("%s and %s are the same file" % (
                src_path, dst_path))
            return True

        logger.info("move: %s -> %s" % (src_path, dst_path))
        if not cls.__dry_run:
            shutil.move(src_path, dst_path)

        return True

    @classmethod
    def chmod(cls, path, permission_text):
        """
        :param str permission_text: "ls -l" style permission string. e.g. -rw-r--r--
        """

        try:
            check_file_existence(path)
        except FileNotFoundError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.debug(e)
            return False

        logger.debug("chmod %s %s" % (path, permission_text))

        os.chmod(path, parseLsPermissionText(permission_text))

    @classmethod
    def rename(cls, src_path, dst_path):
        try:
            check_file_existence(src_path)
        except (InvalidFilePathError, FileNotFoundError):
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return False

        if dataproperty.is_empty_string(dst_path):
            logger.error("empty destination path")
            return False

        if os.path.lexists(dst_path):
            logger.error("'%s' already exists" % (dst_path))
            return False

        logger.info("rename: %s -> %s" % (src_path, dst_path))
        if not cls.__dry_run:
            os.rename(src_path, dst_path)

        return True

    @classmethod
    def remove_directory(cls, path):
        try:
            file_type = check_file_existence(path)
        except (InvalidFilePathError, FileNotFoundError):
            return True

        if file_type not in [FileType.DIRECTORY]:
            logger.error("not a directory: '%s'" % (path))
            return False

        logger.debug("remove directory: " + path)
        if cls.__dry_run:
            return True

        try:
            import shutil
            shutil.rmtree(path, False)
        except (ImportError, IOError):
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return False

        return True

    @classmethod
    def remove_file(cls, path):
        try:
            file_type = check_file_existence(path)
        except (InvalidFilePathError, FileNotFoundError):
            return True

        if file_type not in [FileType.FILE, FileType.LINK]:
            logger.error("not a file: '%s'" % (path))
            return False

        if cls.__dry_run:
            return True

        try:
            os.remove(path)
        except Exception:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return False

        return True

    @classmethod
    def remove_object(cls, path):
        try:
            file_type = check_file_existence(path)
        except (InvalidFilePathError, FileNotFoundError):
            return True

        if file_type not in [FileType.FILE, FileType.LINK]:
            return cls.remove_file(path)

        if file_type not in [FileType.DIRECTORY]:
            return cls.remove_directory(path)

        return False

    @classmethod
    def removeMatchFileRecursively(cls, search_dir_path, re_remove_list):
        logger.debug("remove matched file: search-root=%s, re=%s" % (
            search_dir_path, str(re_remove_list)))

        re_compile_list = [
            re.compile(re_pattern)
            for re_pattern in re_remove_list
            if dataproperty.is_not_empty_string(re_pattern)
        ]

        dict_result_pathlist = {}

        for dir_path, _dir_name_list, filename_list in os.walk(search_dir_path):
            for filename in filename_list:
                for re_pattern in re_compile_list:
                    if re_pattern.search(filename):
                        break
                else:
                    continue

                remove_path = os.path.join(dir_path, filename)
                result = cls.remove_object(remove_path)
                dict_result_pathlist.setdefault(result, []).append(remove_path)

        return dict_result_pathlist

    @classmethod
    def removeMatchDirectory(cls, search_dir_path, re_target_list):
        import shutil

        logger.debug("search-root=%s, target=%s" % (
            search_dir_path, str(re_target_list)))

        dict_result_pathlist = {}

        for dir_path, dir_name_list, _filename_list in os.walk(search_dir_path):
            for dir_name in dir_name_list:
                for re_text in re_target_list:
                    if re_text is None:
                        logger.debug("null regular expression")
                        continue
                    if re.search(re_text, dir_name):
                        break
                else:
                    continue

                remove_path = os.path.join(dir_path, dir_name)
                result = False
                logger.debug("remove directory: " + remove_path)
                if not cls.__dry_run:
                    try:
                        shutil.rmtree(remove_path, False)
                        result = True
                    except (OSError, os.error):
                        # for python 2.5 compatibility
                        _, e, _ = sys.exc_info()
                        logger.exception(e)

                dict_result_pathlist.setdefault(result, []).append(remove_path)

        return dict_result_pathlist


def check_file_existence(path):
    """
    :return: FileType
    :rtype: int
    :raises InvalidFilePathError:
    :raises FileNotFoundError:
    :raises RuntimeError:
    """

    pathvalidate.validate_filename(path)

    if not os.path.lexists(path):
        raise FileNotFoundError(path)

    if os.path.isfile(path):
        logger.debug("file found: " + path)
        return FileType.FILE

    if os.path.isdir(path):
        logger.debug("directory found: " + path)
        return FileType.DIRECTORY

    if os.path.islink(path):
        logger.debug("link found: " + path)
        return FileType.LINK

    raise RuntimeError()


def findFile(search_root_dir_path, re_pattern_text):
    result = findFileAll(
        search_root_dir_path, os.path.isfile, re_pattern_text, find_count=1)

    if dataproperty.is_empty_list_or_tuple(result):
        return None

    return result[0]


def findFileAll(
        search_root_dir_path, check_func,
        re_pattern_text, find_count=six.MAXSIZE):

    re_compile = re.compile(re_pattern_text)
    path_list = []

    for dir_path, dir_name_list, filename_list in os.walk(search_root_dir_path):
        for file_name in dir_name_list + filename_list:
            path = os.path.join(dir_path, file_name)
            if not check_func(path):
                continue

            if re_compile.search(file_name) is None:
                continue

            path_list.append(path)

            if len(path_list) >= find_count:
                return path_list

    logger.debug("find file result: count=%d, files=(%s)" % (
        len(path_list), ", ".join(path_list)))
    return path_list


def findDirectory(search_root_dir_path, re_pattern, find_count=-1):
    result = findFileAll(
        search_root_dir_path, os.path.isdir, re_pattern, find_count=1)

    if dataproperty.is_empty_list_or_tuple(result):
        return None

    return result[0]


def parsePermission3Char(permission):
    """
    'rwx' 形式のアクセス権限文字列 permission を8進数形式に変換する

    :return:
    :rtype: int
    """

    if len(permission) != 3:
        raise ValueError(permission)

    permission_int = 0
    if permission[0] == "r":
        permission_int += 4
    if permission[1] == "w":
        permission_int += 2
    if permission[2] == "x":
        permission_int += 1

    return permission_int


def parseLsPermissionText(permission_text):
    """
    parse "ls -l" style permission text: e.g. -rw-r--r--
    """

    from six.moves import range

    match = re.search("[-drwx]+", permission_text)
    if match is None:
        raise ValueError(
            "invalid permission character: " + permission_text)

    if len(permission_text) != 10:
        raise ValueError(
            "invalid permission text length: " + permission_text)

    permission_text = permission_text[1:]

    return int(
        "0" + "".join([
            str(parsePermission3Char(permission_text[i:i + 3]))
            for i in range(0, 9, 3)
        ]),
        base=8)
