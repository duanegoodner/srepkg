import srepkg.command_input_new as ci_new
import srepkg.repackager_new as rep_new
import srepkg.service_builder as scb


def main(*args):

    srepkg_command = ci_new.SrepkgCommandLine().get_args(*args)
    service_class_builder = scb.ServiceBuilder(srepkg_command)

    repackager = rep_new.Repackager(srepkg_command, service_class_builder)
    repackager.repackage()
