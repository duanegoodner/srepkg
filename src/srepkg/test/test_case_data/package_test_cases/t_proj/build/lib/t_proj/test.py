import argparse


def first_test():

    parser = argparse.ArgumentParser()
    parser.add_argument('thing_to_print')

    args = parser.parse_args()

    print('This is a test, that prints: ', args.thing_to_print)


if __name__ == '__main__':
    first_test()