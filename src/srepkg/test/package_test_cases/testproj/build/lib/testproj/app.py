import argparse
import numpy as np


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('factor', type=int)
    args = parser.parse_args()

    initial_array = np.array([1, 2, 3])
    result = args.factor * initial_array

    print(f'{args.factor} * {initial_array} = {result}')

    print(f'numpy version used by this program = {np.__version__}')


if __name__ == '__main__':
    run()