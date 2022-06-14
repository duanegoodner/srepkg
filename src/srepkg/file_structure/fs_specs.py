from custom_datatypes.named_tuples import SCF, SCD

repackaging_components = \
    [SCD(pname='inner_layer', sc='inner_layer', contents=[
        SCF(pname='orig_pkg_replacement_main.py', sc='main_inner')
    ]),
     SCD(pname='mid_layer', sc='mid_layer', contents=[
         SCD(pname='srepkg_control_components', sc='srepkg_control_components',
             contents=[
                 SCF(pname='__init__.py', sc='srepkg_control_components_init'),
                 SCF(pname='entry_point_runner.py', sc='entry_module'),
                 SCF(pname='srepkg_control_paths.py',
                     sc='srepkg_control_paths'),
                 SCF(pname='srepkg_controller.py', sc='srepkg_controller')
             ]),
         SCF(pname='generic_entry.py', sc='entry_point_template'),
         SCF(pname='srepkg_init.py', sc='srepkg_init'),
         # SCF(pname='srepkg_main.py', sc='main_outer')
     ]),
     SCD(pname='outer_layer', sc='outer_layer', contents=[
         SCF(pname='inner_pkg_installer.py', sc='inner_pkg_installer'),
         SCF(pname='MANIFEST.in.template', sc='manifest_template'),
         SCF(pname='srepkg_setup.py', sc='srepkg_setup_py'),
         SCF(pname='srepkg_starter_setup.cfg', sc='srepkg_setup_cfg'),
     ]),
     SCD(pname='multiple_layers', sc='template_files', contents=[
         SCF(pname='pkg_names.py.template', sc='pkg_names_template')
     ])]


def get_builder_dest(root_name: str = 'dummy_root',
                     srepkg_name: str = 'dummy_srepkg'):
    return [
        SCD(pname=root_name, sc='root', contents=[
            SCD(pname=srepkg_name, sc='srepkg', contents=[
                SCD(pname='srepkg_control_components',
                    sc='srepkg_control_components',
                    contents=[
                        SCF(pname='__init__.py',
                            sc='srepkg_control_components_init'),
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
                # path to inner_pkg depends on orig_pkg file structure so don't
                # even try to predict it here.
                SCF(pname='__init__.py', sc='srepkg_init'),
                # SCF(pname='__main__.py', sc='main_outer'),
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
        ])
    ]
