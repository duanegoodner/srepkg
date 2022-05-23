from srepkg.shared_utils.named_tuples import CSEntry
from srepkg.setup_file_reader import SetupFileType

file_type_only = {
    '.cfg': {
        'raw': {}, 'filtered': {}, 'format_matched': {},
        'final_data': {'file_type': '.cfg'}
    },
    '.py': {
        'raw': {}, 'filtered': {}, 'format_matched': {},
        'final_data': {'file_type': '.py'}
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
            'file_type': '.cfg'
        }
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
        },
        'final_data': {
            'name': 'testproj', 'package_dir': {'': 'src'},
            'console_scripts': ['my_project = testproj.app:run',
                                'my_test = testproj.test:simple_test'],
            'file_type': '.py'
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
            ]},
        'final_data': {
            'name': 'testproj',
            'console_scripts': [
                'my_project = testproj.app:run',
                'my_test = testproj.test:simple_test'
            ],
            'file_type': '.cfg'
        }
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
        },
        'final_data': {
            'name': 'testproj',
            'console_scripts': ['my_project = testproj.app:run',
                                'my_test = testproj.test:simple_test'],
            'file_type': '.py'
        }
    }
}

src_layout_no_cfg = {
    '.cfg': {
        'raw': {},
        'filtered': {},
        'format_matched': {},
        'final_data': {'file_type': '.cfg'}
    },
    '.py': match_src_layout['.py']
}

src_layout_no_py = {
    '.cfg': match_src_layout['.cfg'],
    '.py': {
        'raw': {}, 'filtered': {}, 'format_matched': {},
        'final_data': {'file_type': '.py'}
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
            ]},
        'final_data': {
            'name': 'testproj',
            'console_scripts': [
                'my_project = testproj.app:run',
                'my_test = testproj.test:simple_test'
            ],
            'file_type': '.cfg'
        }
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
        },
        'final_data': {
            'name': 'testproj', 'package_dir': {'': 'src'},
            'file_type': '.py'
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
            'file_type': '.cfg'
        }
    },
    '.py': match_src_layout['.py']
}
