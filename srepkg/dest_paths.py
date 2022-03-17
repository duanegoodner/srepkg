from collections import namedtuple


SCP = namedtuple('SCP', ['pname', 'sc'])

root_name = 't_proj_as_t_projsrnew'
srepkg_name = 't_projsrnew'
inner_pkg_name = 't_proj'


dest_file_structure = \
    [{SCP(pname=root_name, sc='root'): [
        {SCP(pname=srepkg_name, sc='srepkg'): [
            {SCP(pname='srepkg_components', sc='srepkg_components'): [
                SCP(pname='__init__.py', sc='srepkg_components_init'),
                SCP(pname='entry_points.py', sc='entry_module'),
                SCP(pname='srepkg_control_paths.py',
                    sc='srepkg_control_paths'),
                SCP(pname='srepkg_controller.py', sc='srepkg_controller')
            ]
            },
            {SCP(pname='srepkg_entry_points', sc='srepkg_entry_points'): [
                SCP(pname='__init__.py', sc='srepkg_entry_points_init')
            ]
            },
            {SCP(pname=inner_pkg_name, sc='inner_pkg'): [
                SCP(pname='__main__.py', sc='main_inner'),
                SCP(pname='orig_main.py', sc='main_inner_orig'),
                SCP(pname='pkg_names.py', sc='pkg_names_inner')
            ]
            },
            SCP(pname='__init__.py', sc='srepkg_init'),
            SCP(pname='__main__.py', sc='main_outer'),
            SCP(pname='pkg_names.py', sc='pkg_names_mid'),
            SCP(pname='setup.cfg', sc='inner_setup_cfg_active'),
            SCP(pname='setup_off.cfg', sc='inner_setup_cfg_inactive'),
            SCP(pname='setup.py', sc='inner_setup_py_active'),
            SCP(pname='setup_off.py', sc='inner_setup_py_inactive')
        ]
        },
        SCP(pname='inner_pkg_installer.py', sc='inner_pkg_installer'),
        SCP(pname='MANIFEST.in', sc='manifest'),
        SCP(pname='pkg_names.py', sc='pkg_names_outer'),
        SCP(pname='setup.cfg', sc='srepkg_setup_cfg'),
        SCP(pname='setup.py', sc='srepkg_setup_py')
    ]
    }
    ]

