#!/usr/local/bin/python3

import sys
import modes


def main():
    debug = False

    args = sys.argv

    if '--debug' in args:
        debug = True
        args.remove('--debug')

    try:
        mode = modes.get_mode(args[1:])
        mode.run()

    except Exception as e:
        if debug:
            raise e
        else:
            print('Error:', e)


if __name__ == '__main__':
    main()
