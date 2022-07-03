tnonsrc = {
    ".cfg": {
            "name": "tnonsrc",
            "console_scripts": [
                "my_project = tnonsrc.app:run",
                "my_test = tnonsrc.test:first_test",
                "main_entry = tnonsrc.__main__:main",
            ],
    },
    ".py": {},
}

tproj = {
    ".cfg": {
            "name": "tproj",
            "console_scripts": [
                "my_project = tnonsrc.app:run",
                "my_test = tnonsrc.test:first_test",
                "main_entry = tnonsrc.__main__:main",
            ],
    },
    ".py": {},
}

testproj = {
    ".cfg": {
            "name": "testproj",
            "console_scripts": [
                "my_project = testproj.app:run",
                "my_test = testproj.test:simple_test",
            ],
    },
    ".py": {},
}
