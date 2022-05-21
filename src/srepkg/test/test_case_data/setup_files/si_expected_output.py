import src.srepkg.setup_file_reader as sfr

file_type_only = {
    'init': {
        sfr.SetupFileType.PY: {
            'console_scripts': [],
            'file_type': sfr.SetupFileType.PY,
            'package_dir': {},
            'name': None
        },
        sfr.SetupFileType.CFG: {
            'console_scripts': [],
            'file_type': sfr.SetupFileType.CFG,
            'package_dir': {},
            'name': None
        }
    }
}

match_src_layout = {
    'init': {
        sfr.SetupFileType.PY: {
            'console_scripts': ['my_project = testproj.app:run',
                                'my_test = testproj.test:simple_test'],
            'file_type': sfr.SetupFileType.PY,
            'package_dir': {'': 'src'},
            'name': 'testproj'
        },
        sfr.SetupFileType.CFG: {
            'console_scripts': ['my_project = testproj.app:run',
                                'my_test = testproj.test:simple_test'],
            'file_type': sfr.SetupFileType.CFG,
            'package_dir': {'': 'src'},
            'name': 'testproj'
        }
    }
}

match_non_src_layout = {
    'init': {
        sfr.SetupFileType.PY: {
            'console_scripts': ['my_project = testproj.app:run',
                                'my_test = testproj.test:simple_test'],
            'file_type': sfr.SetupFileType.PY,
            'package_dir': {},
            'name': 'testproj'
        },
        sfr.SetupFileType.CFG: {
            'console_scripts': ['my_project = testproj.app:run',
                                'my_test = testproj.test:simple_test'],
            'file_type': sfr.SetupFileType.CFG,
            'package_dir': {},
            'name': 'testproj'
        }
    }
}

src_layout_no_cfg = {
    'init': {
        sfr.SetupFileType.PY: {
            'console_scripts': ['my_project = testproj.app:run',
                                'my_test = testproj.test:simple_test'],
            'file_type': sfr.SetupFileType.PY,
            'package_dir': {'': 'src'},
            'name': 'testproj'
        },
        sfr.SetupFileType.CFG: {
            'console_scripts': [],
            'file_type': sfr.SetupFileType.CFG,
            'package_dir': {},
            'name': None
        }
    }
}

src_layout_no_py = {
    'init': {
        sfr.SetupFileType.PY: {
            'console_scripts': [],
            'file_type': sfr.SetupFileType.PY,
            'package_dir': {},
            'name': None
        },
        sfr.SetupFileType.CFG: {
            'console_scripts': ['my_project = testproj.app:run',
                                'my_test = testproj.test:simple_test'],
            'file_type': sfr.SetupFileType.CFG,
            'package_dir': {'': 'src'},
            'name': 'testproj'
        }
    }
}

mixed_src_layout_valid = {
    'init': {
        sfr.SetupFileType.PY: {
            'console_scripts': [],
            'file_type': sfr.SetupFileType.PY,
            'package_dir': {'': 'src'},
            'name': 'testproj'
        },
        sfr.SetupFileType.CFG: {
            'console_scripts': ['my_project = testproj.app:run',
                                'my_test = testproj.test:simple_test'],
            'file_type': sfr.SetupFileType.CFG,
            'package_dir': {},
            'name': 'testproj'
        }
    }
}
