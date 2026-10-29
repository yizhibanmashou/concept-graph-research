import argparse
from .data import ensure_index

parser = argparse.ArgumentParser()
parser.add_argument('--rebuild', action='store_true')
if __name__ == '__main__':
    args = parser.parse_args()
    ensure_index(force=args.rebuild)
