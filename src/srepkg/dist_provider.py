import abc
import build
import shutil
import sys
from packaging.tags import Tag
from packaging.utils import parse_wheel_filename
from pathlib import Path

import srepkg.orig_src_preparer_interfaces as osp_int


class NullDistProvider(osp_int.DistProviderInterface):

    def __init__(self, *args, **kwargs):
        self._src_path = None
        self._dest_path = None

    def provide(self):
        pass


class DistProviderFromSrc(osp_int.DistProviderInterface):

    # Using build.ProjectBuilder is 10x faster than subprocess
    # Could get another ~40% reduction with threading or multiprocess
    # but at least for small packages, provide() takes less than 1 sed as is

    def __init__(self, src_path: Path, dest_path: Path):
        self._src_path = src_path
        self._dest_path = dest_path

    def provide(self):
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


class DistCopyProvider(osp_int.DistProviderInterface):

    def __init__(self, src_path: Path, dest_path: Path):
        self._src_path = src_path
        self._dest_path = dest_path

    def provide(self):
        shutil.copy2(self._src_path, self._dest_path)
