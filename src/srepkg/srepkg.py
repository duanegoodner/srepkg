import srepkg.command_input as ci
import srepkg.command_input_new as ci_new
import srepkg.repackager as rep
import srepkg.repackager_new as rep_new
import srepkg.service_builder as scb


class SrepkgInput:

    def __init__(self, orig_pkg_ref: str,
                 srepkg_name: str,
                 construction_dir: str,
                 dist_out_dir: str):
        self._orig_pkg_ref = orig_pkg_ref
        self._srepkg_name = srepkg_name
        self._construction_dir = construction_dir
        self._dist_out_dir = dist_out_dir


# class Srepkg:
#     def __init__(self, command_input: SrepkgInput,
#                  service_class_builder: scb.ServiceClassBuilder):
#         self._command_input = command_input
#         self._service_class_builder = service_class_builder


def new_main(*args):

    srepkg_command = ci_new.SrepkgCommandLine().get_args(*args)
    service_class_builder = scb.ServiceBuilder(srepkg_command)

    repackager = rep_new.Repackager(srepkg_command, service_class_builder)


def main(*my_args):
    """
    Builds 'Solo Re-Packaged' (srepkg) version of existing packaged app.
    Command line syntax is:
    $ python_interpreter_path srepkg -m orig_pkg_path [srepkg_name]

    Default value of srepkg_name is: <orig_pkg_name>sr
    'orig_pkg_name' is the basename of orig_pkg_path (and the name of
    the original package)

    SRE-packaged version is saved in:
     ~/srepkg_pkgs/<orig_pkg_name>_srepkg/<srepkg_name>
    """
    args = ci.get_args(*my_args)
    rep.Repackager(
        **vars(args)
        # orig_pkg_ref=args.orig_pkg_ref,
        # srepkg_name=args.srepkg_name,
        # construction_dir=args.construction_dir
    ).repackage()


