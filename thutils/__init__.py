
import thutils.cache
import thutils.common
import thutils.gfile
import thutils.gtime
import thutils.loader
import thutils.logger
import thutils.main
import thutils.option
import thutils.subprocwrapper


def initialize_library(
        program_filename, options, output_dir_path="."):

    import socket

    if output_dir_path == ".":
        if hasattr(options, "output_dir"):
            output_dir_path = options.output_dir

    dry_run = False
    try:
        dry_run = options.dry_run
    except AttributeError:
        pass

    return_value = thutils.logger.logger.initialize(
        program_filename,
        dry_run=dry_run,
        stdout_log_level=options.log_level,
        print_stack_trace=options.stacktrace,
        with_no_log=options.with_no_log,
        output_dir_path=output_dir_path,
    )

    thutils.gfile.FileManager.initialize(dry_run)
    thutils.cache.CommandCache.initialize()

    thutils.logger.logger.debug(
        "complete initialize library: hostname=" + socket.gethostname())
    thutils.logger.logger.debug(
        "options: " + thutils.common.dump_dict(options.__dict__))

    return return_value
