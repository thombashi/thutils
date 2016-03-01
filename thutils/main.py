# encoding: utf-8

'''
@author: Tsuyoshi Hombashi
'''

import os
import sys

import thutils
from thutils.logger import logger


# /usr/include/sysexit.h ---
EX_USAGE = 64      # command line usage error
EX_DATAERR = 65      # data format error
EX_NOINPUT = 66      # cannot open input
EX_NOUSER = 67      # addressee unknown
EX_NOHOST = 68      # host name unknown
EX_UNAVAILABLE = 69      # service unavailable
EX_SOFTWARE = 70      # internal software error
EX_OSERR = 71      # system error (e.g., can't fork)
EX_OSFILE = 72      # critical OS file missing
EX_CANTCREAT = 73      # can't create (user) output file
EX_IOERR = 74      # input/output error
EX_TEMPFAIL = 75      # temp failure; user is invited to retry
EX_PROTOCOL = 76      # remote error in protocol
EX_NOPERM = 77      # permission denied
EX_CONFIG = 78      # configuration error


class Main:
    KEYBOARD_INTERRUPT_FORMAT = "Keyboard Interrupt from %s"

    def __init__(self, function):
        self.function = function

    def __call__(self, *args):
        import thutils.gfile as gfile

        return_value = -1

        try:
            return_value = self.function()
            return return_value
        except (gfile.InvalidFilePathError, gfile.FileNotFoundError):
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return_value = EX_NOINPUT
            return return_value
        except IOError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return_value = EX_IOERR
            return return_value
        except ValueError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return_value = EX_SOFTWARE
            return return_value
        except ImportError:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return_value = EX_OSFILE
            return return_value
        except KeyboardInterrupt:
            logger.info(
                self.KEYBOARD_INTERRUPT_FORMAT % (os.path.basename(__file__)))
            return_value = 1
            return return_value
        except Exception:
            _, e, _ = sys.exc_info()  # for python 2.5 compatibility
            logger.exception(e)
            return_value = 1
            return return_value
        finally:
            logger.debug("exit code: " + str(return_value))
