import argparse
from safe_xiangqigame.xiangqigame.app import app

parser = argparse.ArgumentParser()
parser.add_argument('--use_cur_env', required=False, action="store_true")
args = parser.parse_args()


if __name__ == '__main__':
    app.run()
