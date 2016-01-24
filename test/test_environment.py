# encoding: utf-8

'''
@author: Tsuyoshi Hombashi

:required:
    https://pypi.python.org/pypi/pytest
'''

import os

import pytest

import thutils
from thutils.common import *
from thutils.environment import *


@pytest.fixture
def subproc_wrapper():
    return thutils.subprocwrapper.SubprocessWrapper()

TEST_DIR_PATH = os.path.dirname(os.path.realpath(__file__))


class Test_getGeneralEnvironmentInfoMatrix:

    def test_smoke(self):
        EnvironmentInfo.getGeneralInfoMatrix()


class Test_getGeneralEnvironmentInfoDict:

    def test_smoke(self):
        EnvironmentInfo.getGeneralInfoDict()
