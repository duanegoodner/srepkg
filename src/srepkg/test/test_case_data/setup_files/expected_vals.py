from srepkg.shared_utils.named_tuples import CSEntry

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
    'cfg_format_matched': {
        'name': 'testproj',
        'console_scripts': [
            'my_project = testproj.app:run',
            'my_test = testproj.test:simple_test'
        ]},
}

src_layout_no_cfg_py = match_src_layout_py

src_layout_no_cfg_cfg = {
    'raw': {}, 'filtered': {}, 'format_matched': {}
}

src_layout_no_py_cfg = match_src_layout_cfg

src_layout_no_py_py = {
    'raw': {}, 'filtered': {}, 'format_matched': {}
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
}

mixed_src_layout_invalid_py = match_src_layout_py




