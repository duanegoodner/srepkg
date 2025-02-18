import logging
import shutil
from packaging.tags import Tag
from packaging.utils import parse_wheel_filename
from pathlib import Path

import srepkg.dist_builder as db
import srepkg.error_handling.custom_exceptions as ce
import srepkg.orig_src_preparer_interfaces as osp_int
import srepkg.utils.logged_err_detecting_subprocess as leds

import inner_pkg_installer.yaspin_updater as yu


class DistProviderFromSrc(osp_int.DistProviderInterface):

    def __init__(self, src_path: Path, dest_path: Path):
        self._src_path = src_path
        self._dest_path = dest_path

    def run(self):
        with yu.yaspin_log_updater(
            msg="Building original package wheel from source code",
            logger=logging.getLogger(__name__),
        ):
            wheel_path = db.DistBuilder(
                distribution="wheel",
                source_dir=self._src_path,
                output_directory=self._dest_path,
            ).build()

        wheel_filename = wheel_path.name
        name, version, bld, tags = parse_wheel_filename(wheel_filename)

        if Tag("py3", "none", "any") not in tags:
            with yu.yaspin_log_updater(
                msg="Building original package Sdist from source code",
                logger=logging.getLogger(__name__),
            ):
                db.DistBuilder(
                    distribution="sdist",
                    source_dir=self._src_path,
                    output_directory=self._dest_path,
                ).build()


class DistProviderFromGitRepo(DistProviderFromSrc):
    def __init__(
        self,
        src_path: Path,
        dest_path: Path,
        git_ref: str = None,
        version_command=None,
    ):
        super().__init__(src_path, dest_path)
        self._git_ref = git_ref
        self._version_command = version_command

    def checkout_commit_ref(self):
        if self._git_ref:
            with yu.yaspin_log_updater(
                msg=f"Checking out {self._git_ref}",
                logger=logging.getLogger(__name__),
            ):
                leds.LoggedErrDetectingSubprocess(
                    cmd=["git", "checkout", self._git_ref],
                    gen_logger_name=__name__,
                    std_out_logger_name="std_out",
                    std_err_logger_name="std_err",
                    default_exception=ce.GitCheckoutError,
                    cwd=self._src_path,
                ).run()

    def run(self):
        self.checkout_commit_ref()
        super().run()


class DistCopyProvider(osp_int.DistProviderInterface):

    def __init__(self, src_path: Path, dest_path: Path):
        self._src_path = src_path
        self._dest_path = dest_path

    def run(self):
        with yu.yaspin_log_updater(
            msg=(
                f"Copying {self._src_path.name} into "
                f"srepkg build directory"
            ),
            logger=logging.getLogger(__name__),
        ):
            shutil.copy2(self._src_path, self._dest_path)

        logging.getLogger(__name__).info(
            f"Copied {self._src_path} into {self._dest_path}"
        )
