import abc
import pkginfo
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Union
from wheel_filename import parse_wheel_filename


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
    dists: List[DistInfo] = field(default_factory=lambda: [])
    entry_pts: PkgCSEntryPoints = PkgCSEntryPoints(cs_entry_pts=[])

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
        return self.has_wheel and\
               ('any' in parse_wheel_filename(self.wheel_path.name)
                .platform_tags)

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
    def srepkg_name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def orig_pkg_src_summary(self) -> OrigPkgSrcSummary:
        pass


class SrepkgCompleterInterface(abc.ABC):

    @abc.abstractmethod
    def build_and_cleanup(self):
        pass
