# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

from __future__ import with_statement
import sys
import os.path
import re

import thutils.common as common
from thutils.logger import logger


class FileType:
    FILE = 1
    DIRECTORY = 2
    LINK = 3


class InvalidFilePathError(Exception):
    pass


class FileNotFoundError(Exception):
    pass


class EmptyFileError(Exception):
    pass


RECOVERABLE_ERROR_LIST = (
    InvalidFilePathError, FileNotFoundError, EmptyFileError)


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
        return cls.__re_text.search(cls.get_file_type(file_path)) is not None


class FileManager:
    __dry_run = False

    @classmethod
    def initialize(cls, dry_run):
        cls.__dry_run = dry_run

    @classmethod
    def touch(cls, path):
        logger.debug("touch file: " + path)

        if cls.__dry_run:
            return

        cls.makeDirectory(os.path.dirname(path))

        with open(path, "a") as _fp:
            pass

    @classmethod
    def makeDirectory(cls, path, force=False):
        try:
            check_file_existence(path)
        except (FileNotFoundError, EmptyFileError):
            pass
        except InvalidFilePathError:
            return False
        else:
            logger.debug("already exists: " + path)
            return False

        logger.debug("make directory: " + path)
        if not cls.__dry_run or force:
            os.makedirs(path)

        return True

    @classmethod
    def copyFile(cls, src_path, dst_path):
        import shutil

        try:
            check_file_existence(src_path)
        except FileNotFoundError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.debug(e)
            return False
        except EmptyFileError:
            pass

        dst_file_type = None
        try:
            dst_file_type = check_file_existence(dst_path)
        except:
            pass
        if dst_file_type == FileType.DIRECTORY:
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
        except EmptyFileError:
            pass

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
        permission_text: "ls -l" style permission: e.g. -rw-r--r--
        """

        try:
            check_file_existence(path)
        except FileNotFoundError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.debug(e)
            logger.debug(e)
            return False
        except EmptyFileError:
            pass

        logger.debug("chmod %s %s" % (path, permission_text))

        os.chmod(path, parseLsPermissionText(permission_text))

    @classmethod
    def renameFile(cls, src_path, dst_path):
        if src_path == dst_path:
            logger.debug("no need to rename: src_path == dst_path")
            return True

        try:
            check_file_existence(src_path)
        except (InvalidFilePathError, FileNotFoundError):
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return False

        if common.isEmptyString(dst_path):
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
    def removeDirectory(cls, path):
        if common.isEmptyString(path):
            return False

        if not os.path.isdir(path):
            return False

        logger.debug("remove directory: " + path)
        if not cls.__dry_run:
            try:
                import shutil

                shutil.rmtree(path, False)
            except (ImportError, IOError):
                _, e, _ = sys.exc_info()  # for python 2.5 compatibility
                logger.exception(e)
                return False

        return True

    @classmethod
    def removeFile(cls, path):
        try:
            file_type = check_file_existence(path)
        except (InvalidFilePathError, FileNotFoundError):
            return True

        if file_type in [FileType.FILE, FileType.LINK]:
            if not cls.__dry_run:
                try:
                    os.remove(path)
                except Exception:
                    _, e, _ = sys.exc_info()  # for python 2.5 compatibility
                    logger.exception(e)
                    return False
        elif file_type in [FileType.DIRECTORY]:
            return cls.removeDirectory(path)

        raise ValueError("unknown file type: %s" % (path))

    @classmethod
    def removeMatchFileInDir(cls, search_dir_path, re_target_list):
        logger.debug("remove matched file: search-dir=%s, re=%s" % (
            search_dir_path, str(re_target_list)))

        if common.isEmptyString(search_dir_path) or not os.path.isdir(search_dir_path):
            logger.debug("directory not found: " + str(search_dir_path))
            return {}

        dict_result_pathlist = {}
        for filename in os.listdir(search_dir_path):
            for re_pattern in re_target_list:
                if re.search(re_pattern, filename):
                    break
            else:
                continue

            remove_path = os.path.join(search_dir_path, filename)
            result = cls.removeFile(remove_path)
            dict_result_pathlist.setdefault(result, []).append(remove_path)

        return dict_result_pathlist

    @classmethod
    def removeMatchFileRecursively(cls, search_dir_path, re_remove_list):
        logger.debug("remove matched file: search-root=%s, re=%s" % (
            search_dir_path, str(re_remove_list)))

        if not os.path.isdir(search_dir_path):
            logger.debug("directory not found: " + search_dir_path)
            return {}

        re_compile_list = [
            re.compile(re_pattern)
            for re_pattern in re_remove_list
            if common.isNotEmptyString(re_pattern)
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
                result = cls.removeFile(remove_path)
                dict_result_pathlist.setdefault(result, []).append(remove_path)

        common.debug_dict(dict_result_pathlist, locals())

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
                    except Exception:
                        # for python 2.5 compatibility
                        _, e, _ = sys.exc_info()
                        logger.exception(e)

                dict_result_pathlist.setdefault(result, []).append(remove_path)

        return dict_result_pathlist


def validatePath(path):
    work_path = os.path.normpath(path)

    if common.isEmptyString(path):
        raise InvalidFilePathError("null path")

    if all([w == ".." for w in work_path.split(os.path.sep)]):
        raise InvalidFilePathError(work_path)

    if work_path in ("/", "//"):
        raise InvalidFilePathError("root path")


def check_file_existence(path):
    """
    return value:
            FileType

    raise:
            - InvalidFilePathError
            - FileNotFoundError
            - EmptyFileError
            - RuntimeError
    """

    validatePath(path)

    if not os.path.lexists(path):
        raise FileNotFoundError(path)

    if os.path.isfile(path):
        logger.debug("file found: " + path)
        if os.path.getsize(path) <= 0:
            raise EmptyFileError(path)

        return FileType.FILE

    if os.path.isdir(path):
        logger.debug("directory found: " + path)
        return FileType.DIRECTORY

    if os.path.islink(path):
        logger.debug("link found: " + path)
        return FileType.LINK

    raise RuntimeError()


def getFileNameFromPath(path):
    """
    フルパスから拡張子を除くファイル名を返す。
    """

    # if common.isEmptyString(path):
    #    return ""

    path = path.strip().strip(os.path.sep)

    return os.path.splitext(os.path.basename(path))[0]


def findFile(search_root_dir_path, re_pattern_text):
    result = findFileAll(
        search_root_dir_path, os.path.isfile, re_pattern_text, find_count=1)

    if common.isEmptyListOrTuple(result):
        return None

    return result[0]


def findFileAll(
        search_root_dir_path, check_func,
        re_pattern_text, find_count=sys.maxint):

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

    if common.isEmptyListOrTuple(result):
        return None

    return result[0]


def sanitizeFileName(path, replacement_text=""):
    # if not common.isNotEmptyString(path):
    #    return None

    path = path.strip()
    re_replace = re.compile("[%s]" % re.escape('\:/*?"<>|'))

    return re_replace.sub(replacement_text, path)


def adjustFileName(file_name, replacement_text=""):
    fname = sanitizeFileName(file_name, replacement_text)
    if fname is None:
        return None

    fname = common.RE_SPACE.sub("_", fname)
    return re.sub("[%s]" % (re.escape(",().%")), "", fname)


def parsePermission3Char(permission):
    """
    'rwx' 形式のアクセス権限文字列 permission を8進数形式に変換する

    Return value:
            int
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
