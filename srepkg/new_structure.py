from collections import namedtuple

SCD = namedtuple('SCD', ['pname', 'sc', 'contents'])
SCF = namedtuple('SCF', ['pname', 'sc'])

root_name = 't_proj_as_t_projsrnew'
srepkg_name = 't_projsrnew'
inner_pkg_name = 't_proj'

my_file_structure = \
    [SCD(pname=root_name, sc='root', contents=[
        SCD(pname=srepkg_name, sc='srepkg', contents=[
            SCD(pname='srepkg_components', sc='srepkg_components', contents=[
                SCF(pname='__init__.py', sc='srepkg_components_init'),
                SCF(pname='entry_points.py', sc='entry_module'),
                SCF(pname='srepkg_control_paths.py', sc='srepkg_control_paths'),
                SCF(pname='srepkg_controller.py', sc='srepkg_controller')
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
