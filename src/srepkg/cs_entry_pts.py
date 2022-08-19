import configparser
import shutil
from pathlib import Path
import srepkg.srepkg_builder_ds_and_int as sb_new_int


class EntryPointsBuilder:

    def __init__(
            self,
            orig_pkg_entry_pts: sb_new_int.PkgCSEntryPoints,
            entry_pt_template: Path,
            srepkg_entry_pt_dir: Path,
            srepkg_name: str,
            srepkg_config: configparser.ConfigParser(),
            generic_entry_funct_name: str = 'entry_funct'):
        self._orig_pkg_entry_pts = orig_pkg_entry_pts
        self._entry_pt_template = entry_pt_template
        self._srepkg_entry_pt_dir = srepkg_entry_pt_dir
        self._srepkg_name = srepkg_name
        self._srepkg_config = srepkg_config
        self._generic_entry_funct_name = generic_entry_funct_name

    @property
    def _srepkg_entry_pts(self) -> sb_new_int.PkgCSEntryPoints:
        srepkg_cse_list = [sb_new_int.CSEntryPoint(
            command=orig_pkg_cse.command,
            module=".".join(
                [
                    self._srepkg_name,
                    self._srepkg_entry_pt_dir.name,
                    orig_pkg_cse.command,
                 ]),
            attr=self._generic_entry_funct_name,
            # extras=orig_pkg_cse.extras
        )
            for orig_pkg_cse in self._orig_pkg_entry_pts.cs_entry_pts
        ]
        return sb_new_int.PkgCSEntryPoints(srepkg_cse_list)

    def _write_entry_point_files(self):
        for cse in self._srepkg_entry_pts.cs_entry_pts:
            shutil.copy2(self._entry_pt_template,
                         self._srepkg_entry_pt_dir / f"{cse.command}.py")

        return self

    def _write_entry_point_init(self):
        import_statements = [
            f"import {self._srepkg_name}.srepkg_entry_points.{cse.command}" for
            cse in self._srepkg_entry_pts.cs_entry_pts
        ]

        with (self._srepkg_entry_pt_dir / "__init__.py").open(mode="w") as ei:
            for import_statement in import_statements:
                ei.write("".join([import_statement, "\n"]))
            ei.write("\n")

        return self

    def _update_srepkg_config(self):
        self._srepkg_config.set("options.entry_points", "console_scripts",
                                self._srepkg_entry_pts.as_cfg_string)

        return self

    def build_entry_pts(self):
        self._write_entry_point_files()._write_entry_point_init()\
            ._update_srepkg_config()
