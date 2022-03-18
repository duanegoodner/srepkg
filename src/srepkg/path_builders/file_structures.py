from typing import NamedTuple, List


SCF = NamedTuple('SCF', [('pname', str), ('sc', str)])
SCD = NamedTuple('SCD', [('pname', str), ('sc', str), ('contents', List)])


repackaging_components = \
    [SCD(pname='srepkg_control_components', sc='srepkg_control_components', contents=[
        SCF(pname='__init__.py', sc='srepkg_control_components_init'),
        SCF(pname='entry_points.py', sc='entry_module'),
        SCF(pname='srepkg_control_paths.py', sc='srepkg_control_paths'),
        SCF(pname='srepkg_controller.py', sc='srepkg_controller')
    ]),
     SCF(pname='__init__.py', sc='repackaging_components_init'),
     SCF(pname='entry_point_template.py', sc='entry_point_template'),
     SCF(pname='inner_pkg_installer.py', sc='inner_pkg_installer'),
     SCF(pname='main_inner.py', sc='main_inner'),
     SCF(pname='main_outer.py', sc='main_outer'),
     SCF(pname='MANIFEST.in.template', sc='manifest_template'),
     SCF(pname='pkg_names.py.template', sc='pkg_names_template'),
     SCF(pname='setup.py', sc='srepkg_setup_py'),
     SCF(pname='setup_template.cfg', sc='srepkg_setup_cfg'),
     SCF(pname='srepkg_init.py', sc='srepkg_init')]


def get_builder_dest(root_name: str = 'dummy_root',
                     srepkg_name: str = 'dummy_srepkg',
                     inner_pkg_name: str = 'dummy_inner_pkg'):
    return [
        SCD(pname=root_name, sc='root', contents=[
            SCD(pname=srepkg_name, sc='srepkg', contents=[
                SCD(pname='srepkg_control_components', sc='srepkg_control_components',
                    contents=[
                        SCF(pname='__init__.py', sc='srepkg_control_components_init'),
                        SCF(pname='entry_points.py', sc='entry_module'),
                        SCF(pname='srepkg_control_paths.py',
                            sc='srepkg_control_paths'),
                        SCF(pname='srepkg_controller.py',
                            sc='srepkg_controller')
                    ]),
                SCD(pname='srepkg_entry_points', sc='srepkg_entry_points',
                    contents=[
                        SCF(pname='__init__.py', sc='srepkg_entry_points_init')
                    ]),
                SCD(pname=inner_pkg_name, sc='inner_pkg', contents=[
                    SCF(pname='__main__.py', sc='main_inner'),
                    SCF(pname='orig_main.py', sc='main_inner_orig'),
                    SCF(pname='pkg_names.py', sc='pkg_names_inner')
                ]),
                SCF(pname='__init__.py', sc='srepkg_init'),
                SCF(pname='__main__.py', sc='main_outer'),
                SCF(pname='pkg_names.py', sc='pkg_names_mid'),
                SCF(pname='setup.cfg', sc='inner_setup_cfg_active'),
                SCF(pname='setup_off.cfg', sc='inner_setup_cfg_inactive'),
                SCF(pname='setup.py', sc='inner_setup_py_active'),
                SCF(pname='setup_off.py', sc='inner_setup_py_inactive')
            ]),
            SCF(pname='inner_pkg_installer.py', sc='inner_pkg_installer'),
            SCF(pname='MANIFEST.in', sc='manifest'),
            SCF(pname='pkg_names.py', sc='pkg_names_outer'),
            SCF(pname='setup.cfg', sc='srepkg_setup_cfg'),
            SCF(pname='setup.py', sc='srepkg_setup_py')
        ])]
