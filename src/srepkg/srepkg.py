import srepkg.command_input as ci_new
import srepkg.logging_initializer as lgr
import srepkg.repackager as rep_new
import srepkg.service_builder as scb


def main(*args):

    srepkg_command = ci_new.SrepkgCommandLine().get_args(*args)

    lgr.LoggingInitializer(logfile_dir=srepkg_command.logfile_dir).setup()

    service_class_builder = scb.ServiceBuilder(srepkg_command)

    repackager = rep_new.Repackager(srepkg_command, service_class_builder)
    repackager.repackage()
