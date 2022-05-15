from srepkg.shared_utils.named_tuples import CSEntry

testproj_matched = {
    'py_raw': {
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
    'cfg_raw': {
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
    'py_filtered': {
        'name': 'testproj', 'package_dir': {'': 'src'},
        'console_scripts': ['my_project = testproj.app:run',
                            'my_test = testproj.test:simple_test']
    },
    'cfg_filtered': {
        'name': 'testproj',
        'package_dir': '\n=src',
        'console_scripts': '\nmy_project = testproj.app:run\nmy_test = testproj.test:simple_test'},
    'cfg_format_matched': {
        'name': 'testproj',
        'package_dir': {
            '': 'src'
        },
        'console_scripts': [
            'my_project = testproj.app:run',
            'my_test = testproj.test:simple_test'
        ]},
    'py_with_cse_objs': {
        'name': 'testproj',
        'package_dir': {'': 'src'},
        'console_scripts': [
            CSEntry(
                command='my_project', module_path='testproj.app', funct='run'
            ),
            CSEntry(
                command='my_test', module_path='testproj.test', funct='simple_test'
            )
        ]
    },
    'cfg_with_cse_objs': {
        'name': 'testproj', 'package_dir': {'': 'src'},
        'console_scripts': [
            CSEntry(command='my_project', module_path='testproj.app', funct='run'),
            CSEntry(command='my_test', module_path='testproj.test', funct='simple_test')
        ]
    },
    'merged_params': {
        'name': 'testproj', 'package_dir': {'': 'src'},
        'console_scripts': [
            CSEntry(command='my_project', module_path='testproj.app', funct='run'),
            CSEntry(command='my_test', module_path='testproj.test', funct='simple_test')
        ]
    }
}
