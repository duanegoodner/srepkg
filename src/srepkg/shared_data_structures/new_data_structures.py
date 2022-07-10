import abc
from pathlib import Path


class SrepkgCommand:

    def __init__(self, orig_pkg_ref, srepkg_name, construction_dir, dist_out_dir):
        self.orig_pkg_ref = orig_pkg_ref
        self.srepkg_name = srepkg_name
        self.construction_dir = construction_dir
        self.dist_out_dir = dist_out_dir


class LocalPkgRef(abc.ABC):

    def __init__(self, pkg_path: Path):
        self._pkg_path = pkg_path

    @property
    def pkg_path(self) -> Path:
        return self._pkg_path


class LocalSrcPkgRef(LocalPkgRef):

    def __init__(self, pkg_path: Path):
        super().__init__(pkg_path)


class LocalSdistPkgRef(LocalPkgRef):

    def __init__(self, pkg_path: Path):
        super().__init__(pkg_path)


class LocalWheelPkgRef(LocalPkgRef):

    def __init__(self, pkg_path: Path):
        super().__init__(pkg_path)



