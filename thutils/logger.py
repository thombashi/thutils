'''
@author: Tsuyoshi Hombashi
'''

import sys
import traceback
import os.path
import logging

import dataproperty


class LogLevelText:
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class _BaseWriter(object):
    __MESSAGE_FORMAT = "[%s] %s\n"

    @property
    def write_log(self):
        return self.__write_log

    def __init__(self):
        self.clear_log()

    def clear_log(self):
        self.__write_log = []

    def appendLog(self, log):
        self.__write_log.append(log.rstrip())

    def getLogMessage(self, level, message):
        return self.__MESSAGE_FORMAT % (level, message)

    def writeDebug(self, message):
        raise NotImplementedError()

    def writeInfo(self, message):
        raise NotImplementedError()

    def writeWarn(self, message):
        raise NotImplementedError()

    def writeError(self, message):
        raise NotImplementedError()

    def writeFatal(self, message):
        raise NotImplementedError()


class _LoggingWriter(_BaseWriter):

    def __init__(self):
        super(_LoggingWriter, self).__init__()

    def writeDebug(self, message):
        logging.debug(message)

    def writeInfo(self, message):
        logging.info(message)
        self.appendLog(self.getLogMessage(LogLevelText.INFO, message))

    def writeWarn(self, message):
        logging.warn(message)
        self.appendLog(self.getLogMessage(LogLevelText.WARN, message))

    def writeError(self, message):
        logging.error(message)
        self.appendLog(self.getLogMessage(LogLevelText.ERROR, message))

    def writeFatal(self, message):
        logging.fatal(message)
        self.appendLog(self.getLogMessage(LogLevelText.FATAL, message))


class _StdWriter(_BaseWriter):

    def __init__(self):
        super(_StdWriter, self).__init__()

    def writeDebug(self, message):
        pass

    def writeInfo(self, message):
        message = self.getLogMessage(LogLevelText.INFO, message)
        self.appendLog(message)
        sys.stdout.write(message)

    def writeWarn(self, message):
        message = self.getLogMessage(LogLevelText.WARN, message)
        self.appendLog(message)
        sys.stderr.write(message)

    def writeError(self, message):
        message = self.getLogMessage(LogLevelText.ERROR, message)
        self.appendLog(message)
        sys.stderr.write(message)

    def writeFatal(self, message):
        message = self.getLogMessage(LogLevelText.FATAL, message)
        self.appendLog(message)
        sys.stderr.write(message)


class logger:
    '''
    classdocs
    '''

    LOG_EXTENSION = ".log"
    RE_LogExtension = "\.log$"

    __DEFAULT_OUTPUT_DIR = "."
    __TRACEBACK_FORMAT = "<stack trace>\n%s"

    __writer = _StdWriter()
    __print_stack_trace = False
    __dict_logging_count = {}

    @classmethod
    def initialize(
            cls, program_filename, dry_run, print_stack_trace,
            with_no_log, stdout_log_level, file_log_level=logging.DEBUG,
            output_dir_path="."):

        import path
        import thutils.common as common
        import thutils.gfile as gfile

        cls.__dict_logging_count = {}
        cls.__print_stack_trace = print_stack_trace

        if dataproperty.is_empty_string(output_dir_path) or dry_run:
            output_dir_path = "."

        log_format_base = '[%(levelname)s] %(message)s'
        log_file_path = ""

        if with_no_log:
            args = {
                "level"		: stdout_log_level,
                "format"	: log_format_base,
                "datefmt"	: '%Y-%m-%d %H:%M:%S',
            }
            logging.basicConfig(**args)
        else:
            # set up logging to file

            gfile.FileManager.make_directory(output_dir_path)
            log_file_name = path.Path(
                program_filename).namebase + cls.LOG_EXTENSION
            log_file_path = os.path.join(output_dir_path, log_file_name)

            args = {
                "level"		: file_log_level,
                "format"	:
                    '%(asctime)s %(filename)s(%(lineno)d) %(funcName)s ' +
                    log_format_base,
                "datefmt"	: '%Y-%m-%d %H:%M:%S',
                "filemode"	: 'w',
                "filename"	: log_file_path,
            }
            cls.debug("log file path: " + log_file_path)
            logging.basicConfig(**args)

            # define a Handler which writes INFO messages or higher to the
            # sys.stderr
            console = logging.StreamHandler()
            console.setLevel(stdout_log_level)

            # set a format which is simpler for console use
            formatter = logging.Formatter(log_format_base)

            # tell the handler to use this format
            console.setFormatter(formatter)

            # add the handler to the root logger
            logging.getLogger('').addHandler(console)

        if stdout_log_level == logging.NOTSET:
            logging.disable(logging.FATAL)

        cls.__writer = _LoggingWriter()

        return log_file_path

    @classmethod
    def get_log(cls):
        return cls.__writer.write_log

    @classmethod
    def clear_log(cls):
        cls.__writer.clear_log()

    @classmethod
    def write(cls, msg, log_level, caller=None):
        if caller is None:
            caller = logging.getLogger().findCaller()

        if log_level == logging.DEBUG:
            cls.debug(msg, caller)
        elif log_level == logging.INFO:
            cls.info(msg, caller)
        elif log_level == logging.WARN:
            cls.warn(msg, caller)
        elif log_level == logging.ERROR:
            cls.error(msg, caller)
        elif log_level == logging.FATAL:
            cls.fatal(msg, caller)
        else:
            raise ValueError("invalid log level: " + str(log_level))

    @classmethod
    def info(cls, message, caller=None):
        if caller is None:
            caller = logging.getLogger().findCaller()

        cls.__increment_counter(LogLevelText.INFO)
        cls.__writer.writeInfo(message)

    @classmethod
    def debug(cls, msg, caller=None):
        if caller is None:
            caller = logging.getLogger().findCaller()

        cls.__writer.writeDebug(cls.__get_message(caller, msg))

    @classmethod
    def warn(cls, msg, caller=None):
        if caller is None:
            caller = logging.getLogger().findCaller()

        cls.__increment_counter(LogLevelText.WARN)
        cls.__writer.writeWarn(cls.__get_message(caller, msg))

    @classmethod
    def error(cls, msg, caller=None):
        if caller is None:
            caller = logging.getLogger().findCaller()

        cls.__increment_counter(LogLevelText.ERROR)
        cls.__writer.writeError(cls.__get_message(caller, msg))

    @classmethod
    def exception(cls, exception, msg=""):
        message = "(%s) %s" % (type(exception).__name__, exception)
        if msg != "":
            message += "\n" + msg

        cls.error(message, caller=logging.getLogger().findCaller())

        stack_trace = "<stack trace>" + os.linesep + traceback.format_exc()

        if cls.__print_stack_trace:
            logging.error(stack_trace)
        else:
            logging.debug(stack_trace)

    @classmethod
    def fatal(cls, msg, caller=None):
        if caller is None:
            caller = logging.getLogger().findCaller()

        cls.__increment_counter(LogLevelText.FATAL)
        cls.__writer.writeFatal(cls.__get_message(caller, msg))

        if cls.__print_stack_trace:
            logging.error(cls.__TRACEBACK_FORMAT %
                          (str(traceback.print_exc())))

    @staticmethod
    def __get_message(caller_info_list, msg):
        file_path, line_no, func_name = caller_info_list[:3]
        return "from %s(%d) %s: %s" % (
            os.path.basename(file_path), line_no, str(func_name), str(msg))

    @classmethod
    def __increment_counter(cls, level):
        cls.__dict_logging_count[
            level] = cls.__dict_logging_count.get(level, 0) + 1
