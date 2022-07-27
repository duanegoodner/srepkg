from pathlib import Path


repackaging_components = {
    "mid_layer":            Path("mid_layer"),
    "entry_module":         Path("mid_layer/entry_point_runner.py"),
    "entry_point_template": Path("mid_layer/generic_entry.py"),
    "outer_layer":          Path("outer_layer"),
    "inner_pkg_installer":  Path("outer_layer/inner_pkg_installer.py"),
    "manifest_template":    Path("outer_layer/MANIFEST.in.template"),
    "srepkg_setup_py":      Path("outer_layer/srepkg_setup.py"),
    "srepkg_setup_cfg":     Path("outer_layer/srepkg_starter_setup.cfg")
}


construction_dir = {
    "srepkg_root":              Path("srepkg_root"),
    "inner_pkg_install_cfg":    Path("srepkg_root/inner_pkg_install.cfg"),
    "inner_pkg_installer":      Path("srepkg_root/inner_pkg_installer.py"),
    "manifest":                 Path("srepkg_root/MANIFEST.in"),
    "srepkg_setup_cfg":         Path("srepkg_root/setup.cfg"),
    "srepkg_setup_py":          Path("srepkg_root/setup.py"),
    "srepkg_inner":             Path("srepkg_root/srepkg_inner"),
    "srepkg_init":              Path("srepkg_root/srepkg_inner/__init__.py"),
    "srepkg_entry_points":      Path("srepkg_root/srepkg_inner/srepkg_entry_points"),
    "srepkg_entry_points_init": Path("srepkg_root/srepkg_inner/srepkg_entry_points/__init__.py"),
    "entry_module":             Path("srepkg_root/srepkg_inner/srepkg_entry_points/entry_point_runner.py")

}