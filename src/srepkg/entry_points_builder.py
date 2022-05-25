import shutil
from pathlib import Path
from typing import List
import srepkg.shared_utils as su


class EntryPointsBuilder:
    _gen_entry_funct_name = 'entry_funct'

    def __init__(
            self,
            srepkg_name: str,
            orig_entry_pts: List[su.named_tuples.CSEntry],
            entry_point_template: Path,
            srepkg_entry_pt_dir: Path):
        self._srepkg_name = srepkg_name
        self._orig_entry_pts = orig_entry_pts
        self._entry_point_template = entry_point_template
        self._srepkg_entry_pt_dir = srepkg_entry_pt_dir

    @classmethod
    def from_srepkg_builder_init_args(
            cls,
            orig_pkg_info: su.named_tuples.OrigPkgInfo,
            src_paths: su.named_tuples.BuilderSrcPaths,
            repkg_paths: su.named_tuples.BuilderDestPaths):

        return cls(srepkg_name=repkg_paths.srepkg.name,
                   orig_entry_pts=orig_pkg_info.entry_pts,
                   entry_point_template=src_paths.entry_point_template,
                   srepkg_entry_pt_dir=repkg_paths.srepkg_entry_points)

    def get_cfg_cse_str(self):
        srepkg_cse_list = [
            su.named_tuples.CSEntry(
                command=orig_cse.command,
                module_path='.'.join([
                    self._srepkg_name, self._srepkg_entry_pt_dir.name,
                    orig_cse.command
                ]),
                funct=self._gen_entry_funct_name) for orig_cse in
            self._orig_entry_pts
        ]

        srepkg_cse_str_list = [
            ''.join([cse.command, ' = ', cse.module_path, ':', cse.funct]) for
            cse in srepkg_cse_list
        ]

        return '\n' + '\n'.join(srepkg_cse_str_list)

    def _write_entry_point_files(self):
        for cse in self._orig_entry_pts:
            shutil.copy2(self._entry_point_template, self._srepkg_entry_pt_dir /
                         (cse.command + '.py'))

    def _write_entry_point_init(self):
        entry_pt_imports = [
            f'import {self._srepkg_name}.srepkg_entry_points.{cse.command}' for
            cse in self._orig_entry_pts
        ]

        with open((self._srepkg_entry_pt_dir / '__init__.py'), 'w') as ent_init:
            for import_entry in entry_pt_imports:
                ent_init.write(import_entry + '\n')
            ent_init.write('\n')

    def build_entry_pts(self):
        self._srepkg_entry_pt_dir.mkdir()
        self._write_entry_point_init()
        self._write_entry_point_files()


