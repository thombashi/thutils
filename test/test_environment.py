# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

import os

import pytest

import thutils
from thutils.environment import *


TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class Test_getGeneralEnvironmentInfoMatrix:

    def test_smoke(self):
        EnvironmentInfo.getGeneralInfoMatrix()


class Test_getGeneralEnvironmentInfoDict:

    def test_smoke(self):
        EnvironmentInfo.getGeneralInfoDict()
