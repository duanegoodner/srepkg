import abc
import build
import shutil
import subprocess
import sys
import srepkg.orig_src_preparer_interfaces as osp_int
from srepkg.utils.cd_context_manager import dir_change_to


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
        # with dir_change_to(self._orig_pkg_path):
        #     subprocess.call([
        #         sys.executable, '-m', 'build', '--outdir',
        #         str(self._pkg_receiver.srepkg_inner)])



class DistCopyProvider(ConstructedDistProvider):

    def provide(self):
        shutil.copy2(self._orig_pkg_path, self._pkg_receiver.srepkg_inner)
