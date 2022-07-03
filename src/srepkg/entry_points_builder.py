import shutil
from pathlib import Path
from typing import List

import srepkg.shared_data_structures.named_tuples as nt
import srepkg.shared_data_structures.console_script_entry as cs_ent


class EntryPointsBuilder:

    def __init__(
        self,
        srepkg_name: str,
        orig_entry_pts: List[nt.CSEntryPt],
        entry_point_template: Path,
        srepkg_entry_pt_dir: Path,
        gen_entry_funct_name: str = "entry_funct"
    ):
        self._srepkg_name = srepkg_name
        self._orig_entry_pts = orig_entry_pts
        self._entry_point_template = entry_point_template
        self._srepkg_entry_pt_dir = srepkg_entry_pt_dir
        self._gen_entry_funct_name = gen_entry_funct_name

    @classmethod
    def for_srepkg_task_list_builder(
            cls, builder_info: nt.TaskBuilderInfo):
        return cls(
            srepkg_name=builder_info.repkg_paths.srepkg.name,
            orig_entry_pts=builder_info.orig_pkg_info.entry_pts,
            entry_point_template=builder_info.src_paths.entry_point_template,
            srepkg_entry_pt_dir=builder_info.repkg_paths.srepkg_entry_points
        )

    def get_cfg_cse_str(self):

        srepkg_cse_list = [
            cs_ent.CSEntryPt(
                command=orig_cse.command,
                module_path=".".join(
                    [
                        self._srepkg_name,
                        self._srepkg_entry_pt_dir.name,
                        orig_cse.command,
                    ]
                ),
                funct=self._gen_entry_funct_name,
            )
            for orig_cse in self._orig_entry_pts
        ]

        return cs_ent.CSEntryPoints(srepkg_cse_list).as_cfg_string

    def _write_entry_point_files(self):
        for cse in self._orig_entry_pts:
            shutil.copy2(
                self._entry_point_template,
                self._srepkg_entry_pt_dir / (cse.command + ".py"),
            )

    def _write_entry_point_init(self):
        entry_pt_imports = [
            f"import {self._srepkg_name}.srepkg_entry_points.{cse.command}"
            for cse in self._orig_entry_pts
        ]

        with open((self._srepkg_entry_pt_dir / "__init__.py"), "w") as e_init:
            for import_entry in entry_pt_imports:
                e_init.write(import_entry + "\n")
            e_init.write("\n")

    def build_entry_pts(self):
        self._srepkg_entry_pt_dir.mkdir()
        self._write_entry_point_init()
        self._write_entry_point_files()
