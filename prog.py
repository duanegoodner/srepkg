import argparse


parser = argparse.ArgumentParser()

parser.add_argument(
    'orig_pkg_path',
    type=str,
    help="Path to directory containing original package's setup.cfg file"
)

parser.add_argument(
    '--srepkg_name',
    type=str,
    nargs='?',
    action='store'
)

args = parser.parse_args()

print(args)
