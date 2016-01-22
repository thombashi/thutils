# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required: https://pypi.python.org/pypi/voluptuous
'''

from __future__ import with_statement
import os
import sys

import thutils.common as common
import thutils.gfile as gfile
from thutils.logger import logger


class JsonLoader:

    @staticmethod
    def load(json_file_path, schema=None):
        """
        input:
            json_file_path: path of the json file to be read
            schema: voluptuous schema

        exception:
            - ImportError
            - InvalidFilePathError
            - FileNotFoundError
            - RuntimeError
            - ValueError

        return value:
                dictionary
        """

        try:
            import json
        except ImportError:
            import simplejson as json

        gfile.check_file_existence(json_file_path)

        if not gfile.FileTypeChecker.is_text_file(json_file_path):
            raise ValueError("not a JSON file")

        with open(json_file_path, "r") as fp:
            try:
                dict_json = json.load(fp)
                logger.debug("load json %s:%s" % (
                    json_file_path, common.dump_dict(dict_json)))
            except ValueError:
                _, e, _ = sys.exc_info()  # for python 2.5 compatibility
                raise ValueError(os.linesep.join(
                    [str(e), "decode error: check JSON format with http://jsonlint.com/"]))

        if schema is not None:
            schema(dict_json)

        return dict_json

    @staticmethod
    def loads(json_text, schema=None):
        """
        input:
                json_text: json text to be read
                schema: voluptuous schema

        exception:
                - ImportError
                - RuntimeError
                - ValueError
        """

        try:
            import json
        except ImportError:
            import simplejson as json

        try:
            dict_json = json.loads(json_text)
            logger.debug(
                "load json text:%s" % (common.dump_dict(dict_json)))
        except ValueError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            raise ValueError(os.linesep.join(
                [str(e), "decode error: check JSON format with http://jsonlint.com/"]))

        if schema is not None:
            schema(dict_json)

        return dict_json
