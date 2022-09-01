import subprocess
import tempfile

import build
import shutil
import sys
from packaging.tags import Tag
from packaging.utils import parse_wheel_filename
from pathlib import Path

import srepkg.error_handling.custom_exceptions as ce
import srepkg.orig_src_preparer_interfaces as osp_int


class DistProviderFromSrc(osp_int.DistProviderInterface):

    # Using build.ProjectBuilder is 10x faster than subprocess
    # Could get another ~40% reduction with threading or multiprocess
    # but at least for small packages, provide() takes less than 1 sec as is

    def __init__(self, src_path: Path, dest_path: Path,
                 # temp_dir_obj: tempfile.TemporaryDirectory = None
                 ):
        self._src_path = src_path
        self._dest_path = dest_path
        # self._temp_dir_obj = temp_dir_obj

    def run(self):
        dist_builder = build.ProjectBuilder(
            srcdir=str(self._src_path),
            python_executable=sys.executable)

        # build wheel first
        wheel_path_str = dist_builder.build(
            distribution='wheel',
            output_directory=str(self._dest_path))

        wheel_filename = Path(wheel_path_str).name
        name, version, bld, tags = parse_wheel_filename(wheel_filename)

        # only build sdist if wheel is NOT platform-independent
        if Tag("py3", "none", "any") not in tags:
            dist_builder.build(
                distribution='sdist',
                output_directory=str(self._dest_path))


class DistProviderFromGitRepo(DistProviderFromSrc):
    def __init__(
            self, src_path: Path, dest_path: Path,
            git_ref: str = None, version_command=None):
        super().__init__(src_path, dest_path)
        self._git_ref = git_ref
        self._version_command = version_command

    def _checkout_commit_ref(self):
        if self._git_ref:
            p = subprocess.run(
                ["git", "checkout", self._git_ref],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                cwd=self._src_path
            )
#             TODO send stdout & stderr to log
            if p.returncode != 0:
                raise ce.GitCheckoutError(self._git_ref)

    def run(self):
        self._checkout_commit_ref()
        super().run()


class DistCopyProvider(osp_int.DistProviderInterface):

    def __init__(self, src_path: Path, dest_path: Path):
        self._src_path = src_path
        self._dest_path = dest_path

    def run(self):
        shutil.copy2(self._src_path, self._dest_path)
