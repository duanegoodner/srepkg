import abc
import pkginfo
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List


@dataclass
class CSEntryPoint:
    command: str
    module: str
    attr: str
    extras: List[str]

    @property
    def as_string(self):
        return f"{self.command} = {self.module}:{self.attr}"


@dataclass
class PkgCSEntryPoints:
    cs_entry_pts: List[CSEntryPoint]

    @classmethod
    def from_wheel_inspect_data(cls, wi_data: dict[str, Any]):
        cs_entry_pts = []
        wheel_inspect_epcs =\
            wi_data['dist_info']['entry_points']['console_scripts']
        for key, value in wheel_inspect_epcs.items():
            cs_entry_pts.append(
                CSEntryPoint(
                    command=key,
                    module=value['module'],
                    attr=value['attr'],
                    extras=value['extras']
                )
            )
        return cls(cs_entry_pts)

    @property
    def as_cfg_string(self):
        as_string_list = [cse.as_string for cse in self.cs_entry_pts]
        return "\n" + "\n".join(as_string_list)


@dataclass
class DistInfo:
    path: Path
    dist_obj: pkginfo.Distribution


@dataclass
class OrigPkgSrcSummary:
    pkg_name: str
    pkg_version: str
    dists: List[DistInfo]
    entry_pts: PkgCSEntryPoints = None

    @property
    def has_wheel(self):
        return any([type(dist.dist_obj) == pkginfo.Wheel for dist in
                    self.dists])

    @property
    def wheel_path(self):
        if self.has_wheel:
            return [dist.path for dist in self.dists if type(dist.dist_obj) ==
                    pkginfo.Wheel][0]

    @property
    def has_sdist(self):
        return any([type(dist.dist_obj) == pkginfo.SDist for dist in
                    self.dists])


class SrepkgComponentReceiver(abc.ABC):

    @property
    @abc.abstractmethod
    def srepkg_root(self) -> Path:
        pass

    @property
    @abc.abstractmethod
    def srepkg_inner(self) -> Path:
        pass

    @property
    @abc.abstractmethod
    def srepkg_name(self) -> Path:
        pass

    @property
    @abc.abstractmethod
    def orig_pkg_entry_pts(self) -> PkgCSEntryPoints:
        pass
