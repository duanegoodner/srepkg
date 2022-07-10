import abc
import argparse


class SrepkgInput:

    def __init__(self, orig_pkg_ref: str,
                 srepkg_name: str,
                 construction_dir: str,
                 dist_out_dir: str):
        self._orig_pkg_ref = orig_pkg_ref
        self._srepkg_name = srepkg_name
        self._construction_dir = construction_dir
        self._dist_out_dir = dist_out_dir


class CommandInput(abc.ABC):

    @abc.abstractmethod
    def get_args(self) -> SrepkgInput:
        pass


class SrepkgCommandInput(CommandInput):

    _parser = argparse.ArgumentParser()

    def _attach_args(self):
        self._parser.add_argument(
            "orig_pkg_ref",
            type=str,
            help="A reference to the original package to be repackaged. Can "
                 "be a local path to a directory where a package's setup.py "
                 "resides, a  PyPI package name, or Github repo",
        )

        self._parser.add_argument(
            "-n",
            "--srepkg_name",
            type=str,
            nargs="?",
            action="store",
            help="Name to be used for repackaged package. Default is "
                 "<ORIGINAL_PACKAGE_NAME + srepkg>",
        )

        self._parser.add_argument(
            "-c",
            "--construction_dir",
            type=str,
            nargs="?",
            action="store",
            help="Directory where non-compressed repackage will be built and "
                 "saved. If not specified, srepkg is built in a temp directory "
                 "and deleted after distribution archive creation",
        )

        self._parser.add_argument(
            "-d",
            "--dist_out_dir",
            type=str,
            nargs="?",
            action="store",
            help="Directory where srepkg distribution .zip file is saved. "
                 "Default is the current working directory.",
        )

    def get_args(self, *args) -> SrepkgInput:
        self._attach_args()
        args_namespace = self._parser.parse_args(args)
        return SrepkgInput(**vars(args_namespace))


def main(args):
    my_command_input_object = SrepkgCommandInput()
    return my_command_input_object.get_args(*args)


result = main(['test_arg'])

print(result)

