import logging
import shutil
from packaging.tags import Tag
from packaging.utils import parse_wheel_filename
from pathlib import Path
from yaspin import yaspin

import srepkg.dist_builder as db
import srepkg.error_handling.custom_exceptions as ce
import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.utils.logged_err_detecting_subprocess as leds


class DistProviderFromSrc(osp_int.DistProviderInterface):

    def __init__(self, src_path: Path, dest_path: Path):
        self._src_path = src_path
        self._dest_path = dest_path

    def run(self):

        logging.getLogger(f"std_out.{__name__}").info(
            "Building original package wheel from source code.")

        wheel_path = db.DistBuilder(
            distribution="wheel",
            srcdir=self._src_path,
            output_directory=self._dest_path
        ).build()

        wheel_filename = wheel_path.name
        name, version, bld, tags = parse_wheel_filename(wheel_filename)

        if Tag("py3", "none", "any") not in tags:

            logging.getLogger(f"std_out.{__name__}").info(
                "Building original package sdist from source code")

            db.DistBuilder(
                distribution="sdist",
                srcdir=self._src_path,
                output_directory=self._dest_path
            ).build()


class DistProviderFromGitRepo(DistProviderFromSrc):
    def __init__(
            self, src_path: Path, dest_path: Path,
            git_ref: str = None, version_command=None):
        super().__init__(src_path, dest_path)
        self._git_ref = git_ref
        self._version_command = version_command

    def _checkout_commit_ref(self):
        if self._git_ref:

            leds.LoggedErrDetectingSubprocess(
                cmd=["git", "checkout", self._git_ref],
                gen_logger_name=__name__,
                std_out_logger_name="std_out",
                std_err_logger_name="std_err",
                default_exception=ce.GitCheckoutError,
                cwd=self._src_path
            ).run()

    def run(self):
        self._checkout_commit_ref()
        super().run()


class DistCopyProvider(osp_int.DistProviderInterface):

    def __init__(self, src_path: Path, dest_path: Path):
        self._src_path = src_path
        self._dest_path = dest_path

    def run(self):
        shutil.copy2(self._src_path, self._dest_path)
