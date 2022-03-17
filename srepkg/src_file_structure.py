from .dest_paths import SCP


src_file_structure =\
    [
        {SCP(pname='install_components', sc='install_components'): [
            {SCP(pname='srepkg_components', sc='srepkg_components'): [
                SCP(pname='__init__.py', sc='srepkg_components_init'),
                SCP(pname='entry_points.py', sc='entry_module'),
                SCP(pname='srepkg_control_paths.py', sc='srepkg_control_paths'),
                SCP(pname='srepkg_controller.py', sc='srepkg_controller'),
            ]},
            SCP(pname='__init__.py', sc='install_components_init'),
            SCP(pname='entry_point_template.py', sc='entry_point_template'),
            SCP(pname='inner_pkg_installer.py', sc='inner_pkg_installer'),
            SCP(pname='main_inner.py', sc='main_inner'),
            SCP(pname='main_outer.py', sc='main_outer'),
            SCP(pname='MANIFEST.in.template', sc='manifest_template'),
            SCP(pname='pkg_names.py.template', sc='pkg_names_template'),
            SCP(pname='setup.py', sc='srepkg_setup_py'),
            SCP(pname='setup_template.cfg', sc='srepkg_setup_cfg'),
            SCP(pname='srepkg_init.py', sc='srepkg_init')
        ]}
]