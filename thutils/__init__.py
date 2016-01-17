
import thutils.cache
import thutils.common
import thutils.data_property
import thutils.gfile
import thutils.gtime
import thutils.loader
import thutils.logger
import thutils.main
import thutils.option
import thutils.syswrapper


LIB_TMP_DIR = "/tmp/__golib__"


class NotInstallError(Exception):
    pass


class PermissionError(Exception):
    pass


def initialize_library(
        program_filename, options, output_dir_path="."):

    import socket

    if output_dir_path == ".":
        if hasattr(options, "output_dir"):
            output_dir_path = options.output_dir

    dry_run = False
    if hasattr(options, "dry_run"):
        dry_run = options.dry_run

    return_value = logger.logger.initialize(
        program_filename,
        dry_run=dry_run,
        stdout_log_level=options.log_level,
        print_stack_trace=options.stacktrace,
        with_no_log=options.with_no_log,
        output_dir_path=output_dir_path,
    )

    gfile.FileManager.initialize(dry_run)
    cache.CommandCache.initialize()

    logger.logger.debug(
        "complete initialize library: hostname=" + socket.gethostname())
    logger.logger.debug("options: " + common.dump_dict(options.__dict__))

    return return_value
