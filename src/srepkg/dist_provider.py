import build
import shutil
import subprocess
import sys
from packaging.tags import Tag
from packaging.utils import parse_wheel_filename
from pathlib import Path

import srepkg.error_handling.custom_exceptions as ce
import srepkg.orig_src_preparer_interfaces as osp_int


class DistProviderFromSrc(osp_int.DistProviderInterface):

    def __init__(self, src_path: Path, dest_path: Path):
        self._src_path = src_path
        self._dest_path = dest_path

    def run(self):
        dist_builder = build.ProjectBuilder(
            srcdir=str(self._src_path),
            python_executable=sys.executable)

        # build wheel first
        wheel_path_str = dist_builder.build(
            distribution='wheel',
            output_directory=str(self._dest_path),
            config_settings={"quiet": "quiet"}
        )

        wheel_filename = Path(wheel_path_str).name
        name, version, bld, tags = parse_wheel_filename(wheel_filename)

        if Tag("py3", "none", "any") not in tags:
            dist_builder.build(
                distribution='sdist',
                output_directory=str(self._dest_path),
                config_settings={"--quiet": ""})


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
