"""
Contains the srepkg entry point.
"""

import srepkg.command_input as ci
import srepkg.logging_initializer as lgr
import srepkg.repackager as rep
import srepkg.service_builder as scb


def main(*args) -> None:
    """
    Entry point for srepkg repackaging process. Collect command-line
    arguments, initializes logging, instantiates appropriate
    ServiceBuilder and Repackager, and runs repackaging process.

    Args:
        *args (): entry point args, typically from command line

    Returns:
        None
    """

    srepkg_command = ci.SrepkgCommandLine().get_args(*args)
    logger_initializer = lgr.LoggingInitializer(
        logfile_dir=srepkg_command.logfile_dir
    )
    logger_initializer.setup()
    service_class_builder = scb.ServiceBuilder(srepkg_command)
    repackager = rep.Repackager(srepkg_command, service_class_builder)
    repackager.repackage()
