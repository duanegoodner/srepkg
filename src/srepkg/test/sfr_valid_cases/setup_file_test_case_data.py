import srepkg.shared_data_structures.console_script_entry as cse

match_src_layout = {
    ".cfg": {
            "name": "testproj",
            "console_scripts": [
                "my_project = testproj.app:run",
                "my_test = testproj.test:simple_test",
            ],
    },
    ".py": {
            "name": "testproj",
            "console_scripts": [
                "my_project = testproj.app:run",
                "my_test = testproj.test:simple_test",
            ],
    },
}

match_non_src_layout = {
    ".cfg": {
            "name": "testproj",
            "console_scripts": [
                "my_project = testproj.app:run",
                "my_test = testproj.test:simple_test",
            ],
    },
    ".py": {
            "name": "testproj",
            "console_scripts": [
                "my_project = testproj.app:run",
                "my_test = testproj.test:simple_test",
            ],
    },
}

src_layout_no_cfg = {
    ".cfg": {},
    ".py": match_src_layout[".py"],
}

src_layout_no_py = {
    ".cfg": match_src_layout[".cfg"],
    ".py": {},
}

mixed_src_layout_valid = {
    ".cfg": {
            "name": "testproj",
            "console_scripts": [
                "my_project = testproj.app:run",
                "my_test = testproj.test:simple_test",
            ],
    },
    ".py": {
            "name": "testproj"
    },
}

mixed_src_layout_cse_override = {
    ".cfg": {
            "name": "testproj",
            "console_scripts": [
                "my_project = testproj.app:bad_run",
                "my_test = testproj.test:bad_test",
            ],
    },
    ".py": match_src_layout[".py"],
}


def format_for_merge_and_opi_compare(file_type_dataset: dict):
    """
    Converts dict of data expected from specific setup file to format
    convenient for cfg-py merge followed by comparison w/ OrigPkgInfo.
    file_type_dataset is one of above dicts' '.py' or '.cfg' entries
    """
    exact_item_keys = ["name"]
    final_data = {
        key: file_type_dataset[key]
        for key in exact_item_keys
        if key in file_type_dataset
    }
    if "console_scripts" in file_type_dataset:
        final_data["console_scripts"] = [
            cse.CSEntryPt.from_string(entry)
            for entry in file_type_dataset["console_scripts"]
        ]

    return final_data

