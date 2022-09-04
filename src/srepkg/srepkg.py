import logging
import sys
import tempfile
from pathlib import Path

import srepkg.command_input as ci_new
import srepkg.loggers as lgr
import srepkg.repackager as rep_new
import srepkg.service_builder as scb


def main(*args):
    # logging.basicConfig(
    #     level=logging.DEBUG,
    #     format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    #     filename=str(Path.cwd() / "output.log"),
    #     filemode='w'
    # )
    #
    # console_gen = logging.StreamHandler()
    # console_gen.setLevel(level=logging.WARNING)
    # console_gen_formatter = logging.Formatter(
    #     '%(name)-12s: %(levelname)-8s %(message)s')
    # console_gen.setFormatter(console_gen_formatter)
    # gen_logger = logging.getLogger("gen_logger")
    # gen_logger.addHandler(console_gen)
    #
    # sys.stdout = lgr.StreamLogger(gen_logger.info)
    # sys.stderr = lgr.StreamLogger(gen_logger.error)

    srepkg_command = ci_new.SrepkgCommandLine().get_args(*args)
    service_class_builder = scb.ServiceBuilder(srepkg_command)

    repackager = rep_new.Repackager(srepkg_command, service_class_builder)
    repackager.repackage()
