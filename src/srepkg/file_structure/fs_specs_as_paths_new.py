from pathlib import Path





repackaging_components = {
    "SREPKG_ROOT":          Path("srepkg_root"),
    "manifest_template":    Path("partially_built/MANIFEST.in.template"),
    "srepkg_setup_cfg":     Path("partially_built/srepkg_starter_setup.cfg")
}


construction_dir = {
    "SREPKG_ROOT":              Path("srepkg_root"),
    "inner_pkg_install_cfg":    Path("srepkg_root/inner_pkg_install.cfg"),
    "manifest":                 Path("srepkg_root/MANIFEST.in"),
    "srepkg_setup_cfg":         Path("srepkg_root/setup.cfg"),
    "srepkg_init":              Path("srepkg_root/srepkg_inner/__init__.py"),
    "srepkg_entry_points_init": Path("srepkg_root/srepkg_inner/srepkg_entry_points/__init__.py")
}