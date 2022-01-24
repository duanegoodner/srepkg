import argparse
from subprocess import call

# TODO add ability to choose whether module is installed and/or settle on single option

parser = argparse.ArgumentParser()
parser.add_argument('--run_unsafe', required=False, action="store_true")
args = parser.parse_args()


if __name__ == '__main__' and args.use_cur_env:
    call(['pip', 'install', '-r', 'requirements.txt'])
