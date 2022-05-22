from srepkg.setup_file_reader import SetupFileType

t_nonsrc = {
    SetupFileType.CFG: {
        'format_matched': {
            'name': 't_nonsrc',
            'console_scripts': [
                'my_project = t_nonsrc.app:run',
                'my_test = t_nonsrc.test:first_test',
                'main_entry = t_nonsrc.__main__:main'
            ]
        }
    },
    SetupFileType.PY: {
        'format_matched': {}
    }
}

t_proj = {
    SetupFileType.CFG: {
        'format_matched': {
            'name': 't_proj',
            'console_scripts': [
                'my_project = t_nonsrc.app:run',
                'my_test = t_nonsrc.test:first_test',
                'main_entry = t_nonsrc.__main__:main'
            ]
        }
    },
    SetupFileType.PY: {
        'format_matched': {}
    }
}
