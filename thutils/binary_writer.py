'''
@author: Tsuyoshi Hombashi
'''

import os
import random

import six
from six.moves import range
import dataproperty

from thutils.logger import logger


class BinaryWriter:
    """
    TODO: rename BinaryWriter to DummyBinaryWriter
    """

    __TABLE_SIZE = 16
    __DEFAULT_IO_SIZE = 64 * 1024  # [byte]
    __MAX_IO_SIZE = 1 * 1024 ** 2  # [byte]
    __BYTE_CONTINUITY = 30  # [%]

    def __init__(
            self, io_size_byte=__DEFAULT_IO_SIZE,
            byte_continuity=__BYTE_CONTINUITY):

        self.__verify_size(
            io_size_byte, min_value=1, max_value=self.__MAX_IO_SIZE)

        self.__io_size_byte = int(io_size_byte)  # [byte]
        self.__byte_continuity = byte_continuity  # [%]

        # get open flag ---
        self.__open_flag = self.__get_open_flag()

        # get minimum write data block size ---
        self.__min_data_block_size = 1024
        while True:
            if self.__min_data_block_size < io_size_byte:
                break

            self.__min_data_block_size = int(self.__min_data_block_size / 2)

        logger.debug("""BinaryWriter initialize:
            io-size=%d[byte]
            min-block-size=%d[byte]
        """ % (io_size_byte, self.__min_data_block_size)
        )

        # make write data ---
        random.seed()
        self.__make_binary_data_table()

    def write_binary(
            self, file_path, write_size_byte, permission="-rw-r--r--"):

        return self.__write_binary(
            file_path, write_size_byte, permission)

    def get_write_binary_data(self, size_byte):
        remain_byte = int(size_byte)
        return_data_list = []
        work_data_list = None

        while True:
            if remain_byte < self.__min_data_block_size:
                return_data_list.extend(
                    self.__get_raw_byte_data_list(remain_byte))
                break

            data_idx = random.randint(0, self.__TABLE_SIZE - 1)
            if any([work_data_list is None, not self.__is_continue_byte()]):
                work_data_list = self.__bin_block_data_list[data_idx]
            return_data_list.extend(work_data_list)

            remain_byte -= self.__min_data_block_size

        return return_data_list

    @staticmethod
    def __get_open_flag():
        import platform

        os_type = platform.system()
        if os_type == "Linux":
            return os.O_WRONLY | os.O_CREAT
        elif os_type == "Windows":
            return os.O_WRONLY | os.O_CREAT | os.O_BINARY | os.O_SEQUENTIAL
        else:
            raise OSError("not supported os: " + os_type)

    def __is_continue_byte(self):
        return random.randint(0, 99) < self.__byte_continuity

    def __get_block_size_byte(self, bytes_to_write):
        if bytes_to_write <= 0:
            return 0

        block_size_candidate = self.__io_size_byte

        while True:
            if bytes_to_write >= block_size_candidate:
                return int(block_size_candidate)

            block_size_candidate *= 0.5

            if block_size_candidate < 1.0:
                break

        return 0

    def __get_raw_byte_data_list(self, data_size_byte):
        import struct

        bin_data_list = []

        bin_data = struct.pack("B", random.randint(1, 255))
        for _i in range(data_size_byte):
            if not self.__is_continue_byte():
                bin_data = struct.pack("B", random.randint(1, 255))
            bin_data_list.append(bin_data)

        return bin_data_list

    def __make_binary_data_table(self):
        self.__bin_block_data_list = [
            self.__get_raw_byte_data_list(self.__min_data_block_size)
            for _i in range(self.__TABLE_SIZE)
        ]

    def __verify_size(self, size, min_value=None, max_value=None):
        if dataproperty.is_float(min_value):
            if size < min_value:
                raise ValueError(
                    "invalid size: expected>%d, value=%d" % (min_value, size))

        if dataproperty.is_float(max_value):
            if size > max_value:
                raise ValueError(
                    "invalid size: expected<%d, value=%d" % (max_value, size))

    def __write_binary(
            self, file_path, write_size_byte, permission):
        import thutils.gfile

        self.__verify_size(write_size_byte, min_value=1)

        fd = None
        write_size_byte_count = 0

        try:
            fd = os.open(file_path, self.__open_flag)
            bin_data_list = None

            while True:
                bytes_to_write = write_size_byte - write_size_byte_count
                if bytes_to_write <= 0:
                    break

                io_size_byte = min(
                    int(self.__io_size_byte),
                    self.__get_block_size_byte(bytes_to_write))
                self.__verify_size(io_size_byte, min_value=1)

                if any([bin_data_list is None, not self.__is_continue_byte()]):
                    bin_data_list = self.get_write_binary_data(io_size_byte)

                actual_write_byte = os.write(fd, six.b("").join(bin_data_list))
                if io_size_byte > actual_write_byte:
                    raise IOError(
                        "write failed: write-size=%d[byte] > actual-write=%d[byte]" % (
                            io_size_byte, actual_write_byte))

                write_size_byte_count += actual_write_byte

            os.close(fd)
            fd = None

            thutils.gfile.FileManager.chmod(file_path, permission)

            return write_size_byte_count
        finally:
            if fd is not None:
                os.close(fd)
                fd = None
