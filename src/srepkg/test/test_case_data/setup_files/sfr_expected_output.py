import srepkg.shared_utils.ep_console_script as epcs

file_type_only = {
    '.cfg': {
        'raw': {}, 'filtered': {}, 'format_matched': {}
    },
    '.py': {
        'raw': {}, 'filtered': {}, 'format_matched': {}
    }
}

match_src_layout = {
    '.cfg': {
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
            ]}
    },
    '.py': {
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
        }
    }
}

match_non_src_layout = {
    '.cfg': {
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
            ]}
    },
    '.py': {
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
        }
    }
}

src_layout_no_cfg = {
    '.cfg': {
        'raw': {},
        'filtered': {},
        'format_matched': {}
    },
    '.py': match_src_layout['.py']
}

src_layout_no_py = {
    '.cfg': match_src_layout['.cfg'],
    '.py': {
        'raw': {}, 'filtered': {}, 'format_matched': {}
    }
}

mixed_src_layout_valid = {
    '.cfg': {
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
            ]}
    },
    '.py': {
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
        }
    }
}

mixed_src_layout_cse_override = {
    '.cfg': {
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
            ]}
    },
    '.py': match_src_layout['.py']
}


def get_final_data(file_type_dataset: dict):
    """
    Helper function for use with testing.
    file_type_dataset is one of above dicts' '.py' or '.cfg' entries
    """
    exact_item_keys = ['name', 'package_dir']
    pre_final_data = file_type_dataset['format_matched']
    final_data = {key: pre_final_data[key] for key in exact_item_keys if key in
                  pre_final_data}
    if 'console_scripts' in pre_final_data:
        final_data['console_scripts'] = [
            epcs.parse_cs_line(entry) for entry in
            pre_final_data['console_scripts']
        ]

    return final_data


get_final_data(match_non_src_layout['.py'])
