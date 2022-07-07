from typing import List


class SrepkgConstructionSpecs:

    @property
    def sdist_procedure(self) -> List[str]:
        return [
                'copy_inner_pkg',
                'create_srepkg_init',
                'build_entry_pts',
                'copy_entry_module',
                'build_srepkg_cfg',
                'build_inner_pkg_install_cfg',
                'copy_inner_pkg_installer',
                'copy_srepkg_setup_py',
                'write_manifest',
                'build_distribution'
            ]
