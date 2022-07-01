tnonsrc = {
    ".cfg": {
        "format_matched": {
            "name": "tnonsrc",
            "console_scripts": [
                "my_project = tnonsrc.app:run",
                "my_test = tnonsrc.test:first_test",
                "main_entry = tnonsrc.__main__:main",
            ],
        }
    },
    ".py": {"format_matched": {}},
}

tproj = {
    ".cfg": {
        "format_matched": {
            "name": "tproj",
            "console_scripts": [
                "my_project = tnonsrc.app:run",
                "my_test = tnonsrc.test:first_test",
                "main_entry = tnonsrc.__main__:main",
            ],
        }
    },
    ".py": {"format_matched": {}},
}

testproj = {
    ".cfg": {
        "format_matched": {
            "name": "testproj",
            "console_scripts": [
                "my_project = testproj.app:run",
                "my_test = testproj.test:simple_test",
            ],
        }
    },
    ".py": {"format_matched": {}},
}
