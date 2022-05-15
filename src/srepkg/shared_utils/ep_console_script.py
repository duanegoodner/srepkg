import configparser
from pathlib import Path
from srepkg.shared_utils.named_tuples import CSEntry


def parse_cs_line(cfg_file_line: str):
    [command, full_call] = cfg_file_line.split('=')
    command = command.strip()
    full_call = full_call.strip()
    [module_path, funct] = full_call.split(':')

    return CSEntry(command=command, module_path=module_path, funct=funct)


def build_cs_line(cs_entry: CSEntry, with_redirect=False, new_path: str = None):
    if not with_redirect:
        module_path = cs_entry.module_path
    else:
        if not new_path:
            print('Must provide new_path parameter when with_redirect is True')
            exit(1)
        module_path = new_path

    return cs_entry.command + ' = ' + module_path + ':' + cs_entry.funct


def orig_to_sr_line(orig_line: str, sr_entry_points: str):
    parsed_orig = parse_cs_line(orig_line)
    parsed_sr = CSEntry(
        command=parsed_orig.command + '_sr',
        module_path=Path(sr_entry_points).parent.name + '.' +
        Path(sr_entry_points).name + '.' + parsed_orig.funct,
        funct=parsed_orig.funct)

    return build_cs_line(parsed_sr)


def cfg_cs_list_to_cse_list(cfg_path: Path):
    config = configparser.ConfigParser()
    try:
        config.read(cfg_path)
    except (FileNotFoundError, Exception):
        print('Unable to read .cfg file')

    try:
        ep_cs_list = config['options.entry_points']['console_scripts'] \
            .strip().splitlines()
    except (KeyError, Exception):
        print('Unable to obtain console script entries from .cfg file')

    try:
        cse_list = [parse_cs_line(entry) for entry in ep_cs_list]
    except (TypeError, Exception):
        print('Unable to parse console script entries')

    return cse_list



