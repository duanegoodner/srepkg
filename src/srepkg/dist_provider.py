import abc
import shutil
import subprocess
import sys
# import wheel_inspect
from pathlib import Path
import tempfile
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


class WheelAndSdistProvider(ConstructedDistProvider):

    def provide(self):
        with dir_change_to(self._orig_pkg_path):
            subprocess.call([
                sys.executable, '-m', 'build', '--outdir',
                str(self._pkg_receiver.srepkg_content_path)])


class DistCopyProvider(ConstructedDistProvider):

    def provide(self):
        shutil.copy2(self._orig_pkg_path, self._pkg_receiver.srepkg_content_path)
