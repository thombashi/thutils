# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

from __future__ import with_statement
import os
import sys

try:
    import json
except ImportError:
    import simplejson as json

import thutils.gfile as gfile


class JsonLoader:

    @classmethod
    def load(cls, json_file_path, schema=None):
        """
        :param str json_file_path: Path to the JSON file to be read.
        :param voluptuous.Schema schema: JSON schema.
        :return: Dictionary storing the parse results of JSON.
        :rtype: dictionary

        :raises ImportError:
        :raises InvalidFilePathError:
        :raises FileNotFoundError:
        :raises RuntimeError:
        :raises ValueError:
        """

        gfile.check_file_existence(json_file_path)

        try:
            if not gfile.FileTypeChecker.is_text_file(json_file_path):
                raise ValueError("not a JSON file")
        except ImportError:
            # magicが必要とするライブラリが見つからない (e.g. Windowsでは追加DLLが必要)
            raise

        with open(json_file_path, "r") as fp:
            try:
                dict_json = json.load(fp)
            except ValueError:
                _, e, _ = sys.exc_info()  # for python 2.5 compatibility
                raise ValueError(os.linesep.join([
                    str(e),
                    "decode error: check JSON format with http://jsonlint.com/",
                ]))

        cls.__validate_json(schema, dict_json)

        return dict_json

    @classmethod
    def loads(cls, json_text, schema=None):
        """
        :param str json_text: json text to be parse
        :param voluptuous.Schema schema: JSON schema.
        :return: Dictionary storing the parse results of JSON
        :rtype: dictionary
        :raises ImportError:
        :raises RuntimeError:
        :raises ValueError:
        """

        try:
            json_text = json_text.decode("ascii")
        except AttributeError:
            pass

        try:
            dict_json = json.loads(json_text)
        except ValueError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            raise ValueError(os.linesep.join([
                str(e),
                "decode error: check JSON format with http://jsonlint.com/",
            ]))

        cls.__validate_json(schema, dict_json)

        return dict_json

    @staticmethod
    def __validate_json(schema, dict_json):
        if schema is not None:
            schema(dict_json)
