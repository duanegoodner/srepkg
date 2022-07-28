import abc
import build
import shutil
import sys
import srepkg.orig_src_preparer_interfaces as osp_int


class ConstructedDistProvider(osp_int.DistProviderInterface):

    def __init__(self, orig_pkg_path: str,
                 pkg_receiver: osp_int.WritableSrepkgDirInterface):
        self._orig_pkg_path = orig_pkg_path
        self._pkg_receiver = pkg_receiver

    @abc.abstractmethod
    def provide(self):
        pass


class NullDistProvider(ConstructedDistProvider):

    def provide(self):
        pass


class DistProviderFromSrc(ConstructedDistProvider):

    # Using build.ProjectBuilder is 10x faster than subprocess
    # Could get another ~40% reduction with threading or multiprocess
    # but at least for small packages, provide() takes less than 1 sed as is
    def provide(self):
        dist_builder = build.ProjectBuilder(
            srcdir=self._orig_pkg_path,
            python_executable=sys.executable)
        dist_builder.build(
            distribution='sdist',
            output_directory=str(self._pkg_receiver.srepkg_inner))
        dist_builder.build(
            distribution='wheel',
            output_directory=str(self._pkg_receiver.srepkg_inner)
        )


class DistCopyProvider(ConstructedDistProvider):

    def provide(self):
        shutil.copy2(self._orig_pkg_path, self._pkg_receiver.srepkg_inner)
