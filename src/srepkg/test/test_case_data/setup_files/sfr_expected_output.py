from srepkg.shared_utils.named_tuples import CSEntry
from src.srepkg.setup_file_reader import SetupFileType


file_type_only_py = {
    'raw': {}, 'filtered': {}, 'format_matched': {},
    'final_data': {'file_type': SetupFileType.PY}
}

file_type_only_cfg = {
    'raw': {}, 'filtered': {}, 'format_matched': {},
    'final_data': {'file_type': SetupFileType.CFG}
}

match_src_layout_py = {
    'raw': {
        'name': 'testproj',
        'package_dir': {
            '': 'src'
        },
        'packages': [
            'test_case_data',
            't_utils'
        ],
        'install_requires': [
            'numpy >= 1.22',
            'pandas'
        ],
        'entry_points': {
            'console_scripts': [
                'my_project = testproj.app:run',
                'my_test = testproj.test:simple_test'
            ]
        }
    },
    'filtered': {
        'name': 'testproj', 'package_dir': {'': 'src'},
        'console_scripts': ['my_project = testproj.app:run',
                            'my_test = testproj.test:simple_test']
    },
    'format_matched': {
        'name': 'testproj', 'package_dir': {'': 'src'},
        'console_scripts': ['my_project = testproj.app:run',
                            'my_test = testproj.test:simple_test']
    },
    'final_data': {
        'name': 'testproj', 'package_dir': {'': 'src'},
        'console_scripts': ['my_project = testproj.app:run',
                            'my_test = testproj.test:simple_test'],
        'file_type': SetupFileType.PY
    }
}

match_src_layout_cfg = {
    'raw': {
        'metadata':
            {
                'name': 'testproj'
            },
        'options': {'package_dir': '\n=src',
                    'packages': 'find:',
                    'install_requires': '\nnumpy >= 1.22\npandas'
                    },
        'options.packages.find':
            {
                'where': 'src'
            },
        'options.entry_points':
            {
                'console_scripts': '\nmy_project = testproj.app:run\nmy_test = testproj.test:simple_test'
            }
    },
    'filtered': {
        'name': 'testproj',
        'package_dir': '\n=src',
        'console_scripts': '\nmy_project = testproj.app:run\nmy_test = testproj.test:simple_test'},
    'format_matched': {
        'name': 'testproj',
        'package_dir': {
            '': 'src'
        },
        'console_scripts': [
            'my_project = testproj.app:run',
            'my_test = testproj.test:simple_test'
        ]},
    'final_data': {
        'name': 'testproj',
        'package_dir': {
            '': 'src'
        },
        'console_scripts': [
            'my_project = testproj.app:run',
            'my_test = testproj.test:simple_test'
        ],
        'file_type': SetupFileType.CFG
    }
}

match_non_src_layout_py = {
    'raw': {
        'name': 'testproj',
        'packages': [
            'test_case_data',
            't_utils'
        ],
        'install_requires': [
            'numpy >= 1.22',
            'pandas'
        ],
        'entry_points': {
            'console_scripts': [
                'my_project = testproj.app:run',
                'my_test = testproj.test:simple_test'
            ]
        }
    },
    'filtered': {
        'name': 'testproj',
        'console_scripts': ['my_project = testproj.app:run',
                            'my_test = testproj.test:simple_test']
    },
    'format_matched': {
        'name': 'testproj',
        'console_scripts': ['my_project = testproj.app:run',
                            'my_test = testproj.test:simple_test']
    },
    'final_data': {
        'name': 'testproj',
        'console_scripts': ['my_project = testproj.app:run',
                            'my_test = testproj.test:simple_test'],
        'file_type': SetupFileType.PY
    }
}

match_non_src_layout_cfg = {
    'raw': {
        'metadata':
            {
                'name': 'testproj'
            },
        'options': {'packages': 'find:',
                    'install_requires': '\nnumpy >= 1.22\npandas'
                    },
        'options.entry_points':
            {
                'console_scripts': '\nmy_project = testproj.app:run\nmy_test = testproj.test:simple_test'
            }
    },
    'filtered': {
        'name': 'testproj',
        'console_scripts': '\nmy_project = testproj.app:run\nmy_test = testproj.test:simple_test'},
    'format_matched': {
        'name': 'testproj',
        'console_scripts': [
            'my_project = testproj.app:run',
            'my_test = testproj.test:simple_test'
        ]},
    'final_data': {
        'name': 'testproj',
        'console_scripts': [
            'my_project = testproj.app:run',
            'my_test = testproj.test:simple_test'
        ],
        'file_type': SetupFileType.CFG
    }
}

src_layout_no_cfg_py = match_src_layout_py

src_layout_no_cfg_cfg = {
    'raw': {},
    'filtered': {},
    'format_matched': {},
    'final_data': {'file_type': SetupFileType.CFG}
}

src_layout_no_py_cfg = match_src_layout_cfg

src_layout_no_py_py = {
    'raw': {}, 'filtered': {}, 'format_matched': {},
    'final_data': {'file_type': SetupFileType.PY}
}

mixed_src_layout_valid_cfg = {
    'raw': {
        'metadata':
            {
                'name': 'testproj'
            },
        'options': {'packages': 'find:',
                    'install_requires': '\nnumpy >= 1.22\npandas'
                    },
        'options.entry_points':
            {
                'console_scripts': '\nmy_project = testproj.app:run\nmy_test = testproj.test:simple_test'
            }
    },
    'filtered': {
        'name': 'testproj',
        'console_scripts': '\nmy_project = testproj.app:run\nmy_test = testproj.test:simple_test'},
    'format_matched': {
        'name': 'testproj',
        'console_scripts': [
            'my_project = testproj.app:run',
            'my_test = testproj.test:simple_test'
        ]},
    'final_data': {
        'name': 'testproj',
        'console_scripts': [
            'my_project = testproj.app:run',
            'my_test = testproj.test:simple_test'
        ],
        'file_type': SetupFileType.CFG
    }
}

mixed_src_layout_valid_py = {
    'raw': {
        'name': 'testproj',
        'package_dir': {
            '': 'src'
        },
        'packages': [
            'test_case_data',
            't_utils'
        ],
        'install_requires': [
            'numpy >= 1.22',
            'pandas'
        ]
    },
    'filtered': {
        'name': 'testproj', 'package_dir': {'': 'src'},
    },
    'format_matched': {
        'name': 'testproj', 'package_dir': {'': 'src'}
    },
    'final_data': {
        'name': 'testproj', 'package_dir': {'': 'src'},
        'file_type': SetupFileType.PY
    }
}

mixed_src_layout_invalid_cfg = {
    'raw': {
        'metadata':
            {
                'name': 'testproj'
            },
        'options': {'package_dir': '\n=src',
                    'packages': 'find:',
                    'install_requires': '\nnumpy >= 1.22\npandas'
                    },
        'options.packages.find':
            {
                'where': 'src'
            },
        'options.entry_points':
            {
                'console_scripts': '\nmy_project = testproj.app:bad_run\nmy_test = testproj.test:bad_test'
            }
    },
    'filtered': {
        'name': 'testproj',
        'package_dir': '\n=src',
        'console_scripts': '\nmy_project = testproj.app:bad_run\nmy_test = testproj.test:bad_test'},
    'format_matched': {
        'name': 'testproj',
        'package_dir': {
            '': 'src'
        },
        'console_scripts': [
            'my_project = testproj.app:bad_run',
            'my_test = testproj.test:bad_test'
        ]},
    'final_data': {
        'name': 'testproj',
        'package_dir': {
            '': 'src'
        },
        'console_scripts': [
            'my_project = testproj.app:bad_run',
            'my_test = testproj.test:bad_test'
        ],
        'file_type': SetupFileType.CFG
    }
}

mixed_src_layout_invalid_py = match_src_layout_py




