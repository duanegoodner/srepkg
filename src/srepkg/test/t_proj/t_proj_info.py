from pathlib import Path
import srepkg.shared_utils as su

pkg_name = 't_proj'
pkg_root = Path(__file__).parent.absolute()
cse_string = '\nmy_project = t_proj.app:run' \
             '\nmy_test = t_proj.test:first_test' \
             '\nmain_entry = t_proj.__main__:main'
cse_list = [su.ep_console_script.parse_cs_line(entry) for entry in
            cse_string.strip().split('\n')]
