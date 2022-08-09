import configparser
import shutil

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


class CSEntryPointUtil:

    @staticmethod
    def read(wheel_inspect_epcs: dict):
        return PkgCSEntryPoints.from_wheel_inspect_data(wheel_inspect_epcs)

    @staticmethod
    def write(pkg_cs_entry_pts: PkgCSEntryPoints):
        return pkg_cs_entry_pts.as_cfg_string


class EntryPointsBuilder:

    def __init__(
            self,
            wheel_inspect_data: dict[str, Any],
            entry_pt_template: Path,
            srepkg_entry_pt_dir: Path,
            srepkg_name: str,
            srepkg_config: configparser.ConfigParser(),
            generic_entry_funct_name: str = "entry_funct"):
        self._entry_pt_template = entry_pt_template
        self._srepkg_entry_pt_dir = srepkg_entry_pt_dir
        self._srepkg_name = srepkg_name
        self._srepkg_config = srepkg_config
        self._generic_entry_funct_name = generic_entry_funct_name
        self._entry_pt_objs = PkgCSEntryPoints.from_wheel_inspect_data(
            wheel_inspect_data)

    def _write_entry_point_files(self):
        for cse in self._entry_pt_objs.cs_entry_pts:
            shutil.copy2(self._entry_pt_template,
                         self._srepkg_entry_pt_dir / f"{cse.command}.py")

        return self

    def _write_entry_point_init(self):
        import_statements = [
            f"import {self._srepkg_name}.srepkg_entry_points.{cse.command}" for
            cse in self._entry_pt_objs.cs_entry_pts
        ]

        with (self._srepkg_entry_pt_dir / "__init__.py").open(mode="w") as ei:
            for import_statement in import_statements:
                ei.write("".join([import_statement, "\n"]))
            ei.write("\n")

        return self

    def _update_srepkg_config(self):
        self._srepkg_config.set("options.entry_points", "console_scripts",
                                self._entry_pt_objs.as_cfg_string)

        return self

    def build_entry_pts(self):
        self._write_entry_point_files()._write_entry_point_init()\
            ._update_srepkg_config()
