import argparse
import numpy as np


def run():
    parser = argparse.ArgumentParser(
        description='Multiplies the numpy array [1 2 3] by a user-provided '
                    'integer. Displays the resulting array as well as the '
                    'version of numpy used.')
    parser.add_argument(
        'factor',
        type=int,
        help='An integer that numpy array [1 2 3] will be multiplied by'

    )
    args = parser.parse_args()

    initial_array = np.array([1, 2, 3])
    result = args.factor * initial_array

    print(f'{args.factor} * {initial_array} = {result}')

    print(f'numpy version used by this program = {np.__version__}')


if __name__ == '__main__':
    run()
