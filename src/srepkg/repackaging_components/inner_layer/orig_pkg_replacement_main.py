import subprocess
import sys
from .pkg_names import inner_pkg_name


def main():

    # extract args from sys.argv instead of using argparse to easily preserve
    # user's arg order when passing on to orig_main.py
    #
    # sys.argv as called by outer main:
    # [path_to_this_file, --called_by_safe_pkg, venv_pkg_path, *pkg_args]

    outer_main_call_key = sys.argv[1]
    venv_site_pkgs = sys.argv[2]
    pkg_args = sys.argv[3:]

    if outer_main_call_key == "--called_by_safe_pkg":
        subprocess.call(
            [sys.executable, venv_site_pkgs + f"/{inner_pkg_name}/orig_main.py"]
            + pkg_args
        )


if __name__ == "__main__":
    main()
