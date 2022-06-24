from custom_datatypes.named_tuples import SCF, SCD

repackaging_components = [
    SCD(
        pname="mid_layer",
        sc="mid_layer",
        contents=[
            SCF(pname="entry_point_runner.py", sc="entry_module"),
            SCF(pname="generic_entry.py", sc="entry_point_template"),
            SCF(pname="srepkg_init.py", sc="srepkg_init"),
        ],
    ),
    SCD(
        pname="outer_layer",
        sc="outer_layer",
        contents=[
            SCF(pname="inner_pkg_installer.py", sc="inner_pkg_installer"),
            SCF(pname="MANIFEST.in.template", sc="manifest_template"),
            SCF(pname="srepkg_setup.py", sc="srepkg_setup_py"),
            SCF(pname="srepkg_starter_setup.cfg", sc="srepkg_setup_cfg"),
        ],
    )
]


def get_srepkg_root(srepkg_name: str = "dummy_srepkg_name"):
    return [
        SCD(
            pname=srepkg_name,
            sc="srepkg",
            contents=[
                SCD(
                    pname="srepkg_entry_points",
                    sc="srepkg_entry_points",
                    contents=[
                        SCF(
                            pname="__init__.py",
                            sc="srepkg_entry_points_init",
                        ),
                        SCF(pname="entry_point_runner.py",
                            sc="entry_module"),
                    ],
                ),
                SCF(pname="__init__.py", sc="srepkg_init"),
            ],
        ),
        SCF(pname="inner_pkg_install.cfg", sc="inner_pkg_install_cfg"),
        SCF(pname="inner_pkg_installer.py", sc="inner_pkg_installer"),
        SCF(pname="MANIFEST.in", sc="manifest"),
        SCF(pname="setup.cfg", sc="srepkg_setup_cfg"),
        SCF(pname="setup.py", sc="srepkg_setup_py")
    ]


def get_builder_dest(
        root_name: str = "dummy_root", srepkg_name: str = "dummy_srepkg"
):
    return [
        SCD(
            pname=root_name,
            sc="root",
            contents=[
                SCD(
                    pname=srepkg_name,
                    sc="srepkg",
                    contents=[
                        SCD(
                            pname="srepkg_entry_points",
                            sc="srepkg_entry_points",
                            contents=[
                                SCF(
                                    pname="__init__.py",
                                    sc="srepkg_entry_points_init",
                                ),
                                SCF(pname="entry_point_runner.py",
                                    sc="entry_module"),
                            ],
                        ),
                        SCF(pname="__init__.py", sc="srepkg_init"),
                    ],
                ),
                SCF(pname="inner_pkg_install.cfg", sc="inner_pkg_install_cfg"),
                SCF(pname="inner_pkg_installer.py", sc="inner_pkg_installer"),
                SCF(pname="MANIFEST.in", sc="manifest"),
                SCF(pname="setup.cfg", sc="srepkg_setup_cfg"),
                SCF(pname="setup.py", sc="srepkg_setup_py"),
            ],
        )
    ]
