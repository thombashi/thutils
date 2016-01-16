# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

import thutils.common as common


class Typecode:
    NONE = 0
    INT = 1 << 0
    FLOAT = 1 << 1
    STRING = 1 << 2

    @classmethod
    def getTypecodeFromBitmap(cls, typecode_bitmap):
        typecode_list = [cls.STRING, cls.FLOAT, cls.INT]

        for typecode in typecode_list:
            if typecode_bitmap & typecode:
                return typecode

        return cls.STRING


class Align:

    class __AlignData:

        @property
        def align_code(self):
            return self.__align_code

        @property
        def align_string(self):
            return self.__align_string

        def __init__(self, code, string):
            self.__align_code = code
            self.__align_string = string

    AUTO = __AlignData(1 << 0, "auto")
    LEFT = __AlignData(1 << 1, "left")
    RIGHT = __AlignData(1 << 2, "right")
    CENTER = __AlignData(1 << 3, "center")


class DataPeroperty(common.BaseObject):

    @property
    def data(self):
        return self.__data

    @property
    def typecode(self):
        return self.__typecode

    @property
    def align(self):
        return self.__align

    @property
    def str_len(self):
        return self.__str_len

    @property
    def integer_digits(self):
        return self.__integer_digits

    @property
    def decimal_places(self):
        return self.__decimal_places

    @property
    def additional_format_len(self):
        return self.__additional_format_len

    @property
    def type_format(self):
        return self.__type_format

    def __init__(self, data):
        super(DataPeroperty, self).__init__()

        self.__data = data
        self.__typecode = self.__get_typecode(data)
        self.__align = PropertyExtractor.getAlignFromTypeCode(self.__typecode)

        integer_digits, decimal_places = common.get_number_of_digit(data)
        self.__integer_digits = integer_digits
        self.__decimal_places = decimal_places
        self.__additional_format_len = PropertyExtractor.getAdditionalFormatLen(
            data)

        self.__type_format = PropertyExtractor.getTypeFormat(
            data, decimal_places)
        self.__str_len = self.__get_str_len()

    @staticmethod
    def __get_typecode(data):
        if data is None:
            return Typecode.NONE

        if common.isInteger(data):
            return Typecode.INT

        if common.isFloat(data):
            return Typecode.FLOAT

        return Typecode.STRING

    def __get_str_len(self):
        if self.typecode == Typecode.INT:
            return (
                self.integer_digits +
                PropertyExtractor.getAdditionalFormatLen(self.data))

        if self.typecode == Typecode.FLOAT:
            return (
                PropertyExtractor.getBaseFloatLen(
                    self.integer_digits, self.decimal_places) +
                PropertyExtractor.getAdditionalFormatLen(self.data))

        return common.getTextLen(self.data)


class ColumnDataPeroperty(common.BaseObject):

    @property
    def typecode(self):
        return Typecode.getTypecodeFromBitmap(self.typecode_bitmap)

    @property
    def align(self):
        return PropertyExtractor.getAlignFromTypeCode(self.typecode)

    @property
    def padding_len(self):
        return self.__str_len

    @property
    def decimal_places(self):
        import math

        avg = self.minmax_decimal_places.average()
        if common.isNaN(avg):
            return float("nan")

        return int(math.ceil(avg))

    def __init__(self):
        self.typecode_bitmap = Typecode.NONE
        self.__str_len = 0
        self.type_format = None
        self.minmax_integer_digits = common.MinMaxObject()
        self.minmax_decimal_places = common.MinMaxObject()
        self.minmax_additional_format_len = common.MinMaxObject()

    def update_padding_len(self, padding_len):
        self.__str_len = max(self.__str_len, padding_len)

    def update_header(self, prop):
        self.update_padding_len(prop.str_len)

        if prop.typecode in (Typecode.FLOAT, Typecode.INT):
            self.minmax_integer_digits.update(prop.integer_digits)

        if prop.typecode == Typecode.FLOAT:
            self.minmax_decimal_places.update(prop.decimal_places)

        self.minmax_additional_format_len.update(prop.additional_format_len)

    def update_body(self, prop):
        self.typecode_bitmap |= prop.typecode
        self.update_header(prop)


class PropertyExtractor:
    __dict_ValueType_Align = {
        Typecode.STRING	: Align.LEFT,
        Typecode.INT	: Align.RIGHT,
        Typecode.FLOAT	: Align.RIGHT,
    }

    @classmethod
    def getAlignFromTypeCode(cls, typecode):
        return cls.__dict_ValueType_Align.get(typecode, Align.LEFT)

    @staticmethod
    def getTypeFormat(value, decimal_places):
        if common.isInteger(value):
            return "d"
        if common.isFloat(value):
            if common.isNaN(value):
                return "f"
            return ".%df" % (decimal_places)
        return "s"

    @staticmethod
    def getBaseFloatLen(integer_digits, decimal_places):
        float_len = integer_digits + decimal_places
        if decimal_places > 0:
            # for dot
            float_len += 1
        return float_len

    @staticmethod
    def getAdditionalFormatLen(data):
        if not common.isFloat(data):
            return 0

        format_len = 0

        if data < 0:
            # for minus character
            format_len += 1

        return format_len

    @staticmethod
    def extractDataPropertyList(data_list):
        if common.isEmptyListOrTuple(data_list):
            return []

        return [DataPeroperty(data) for data in data_list]

    @classmethod
    def extractDataPropertyMatrix(cls, data_matrix):
        return [
            cls.extractDataPropertyList(data_list)
            for data_list in data_matrix
        ]

    @classmethod
    def extractColumnPropertyList(cls, header_list, data_matrix):
        data_prop_matrix = cls.extractDataPropertyMatrix(data_matrix)
        header_prop_list = cls.extractDataPropertyList(header_list)
        column_prop_list = []

        # for header_prop, col_prop_list in zip(header_prop_list,
        # zip(*data_prop_matrix)):
        for col_idx, col_prop_list in enumerate(zip(*data_prop_matrix)):
            column_prop = ColumnDataPeroperty()

            if common.isNotEmptyListOrTuple(header_prop_list):
                header_prop = header_prop_list[col_idx]
                column_prop.update_header(header_prop)

            for prop in col_prop_list:
                column_prop.update_body(prop)

            decimal_places = 0
            if column_prop.typecode == Typecode.FLOAT:
                decimal_places = column_prop.decimal_places

                float_len = (
                    cls.getBaseFloatLen(
                        column_prop.minmax_integer_digits.max_value,
                        decimal_places) +
                    column_prop.minmax_additional_format_len.max_value
                )
                column_prop.update_padding_len(float_len)

            column_prop.type_format = cls.__get_column_type_format(
                column_prop.typecode, decimal_places)

            column_prop_list.append(column_prop)

        return column_prop_list

    @staticmethod
    def __get_column_type_format(typecode, decimal_places):
        if typecode == Typecode.INT:
            return "d"
        if typecode == Typecode.FLOAT:
            if common.isNaN(decimal_places):
                return "f"
            return ".%df" % (decimal_places)
        return "s"
