import pkginfo
from dataclasses import dataclass, field
from packaging.utils import parse_wheel_filename
from pathlib import Path
from typing import List, NamedTuple, Union


@dataclass
class CSEntryPoint:
    command: str
    module: str
    attr: str
    # extras: List[str]

    @property
    def as_string(self):
        return f"{self.command} = {self.module}:{self.attr}"


@dataclass
class PkgCSEntryPoints:
    cs_entry_pts: List[CSEntryPoint]

    @property
    def as_cfg_string(self):
        as_string_list = [cse.as_string for cse in self.cs_entry_pts]
        return "\n" + "\n".join(as_string_list)


@dataclass
class DistInfo:
    path: Path
    dist_obj: pkginfo.Distribution


class UniquePkg(NamedTuple):
    name: str
    version: str


@dataclass
class OrigPkgSrcSummary:
    pkg_name: str
    pkg_version: str
    dists: List[DistInfo] = field(default_factory=lambda: [])
    entry_pts: PkgCSEntryPoints = field(
        default_factory=lambda: PkgCSEntryPoints(cs_entry_pts=[]))

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
    def has_platform_indep_wheel(self):
        if not self.has_wheel:
            return False
        name, version, bld, tag = parse_wheel_filename(self.wheel_path.name)
        return list(tag)[0].platform == "any"

    @property
    def has_sdist(self):
        return any([type(dist.dist_obj) == pkginfo.SDist for dist in
                    self.dists])

    @property
    def sdist_path(self):
        if self.has_sdist:
            return [dist.path for dist in self.dists if type(dist.dist_obj) ==
                    pkginfo.SDist][0]

    @property
    def src_for_srepkg_wheel(self) -> Union[Path, None]:
        if self.has_wheel:
            return self.wheel_path
        if self.has_sdist:
            return self.sdist_path

    @property
    def src_for_srepkg_sdist(self) -> Union[Path, None]:
        if self.has_platform_indep_wheel:
            return self.wheel_path
        if self.has_sdist:
            return self.sdist_path
