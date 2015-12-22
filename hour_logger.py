#!/usr/local/bin/python3

import sys
import modes

def main():
    mode = modes.get_mode(sys.argv[1:])
    mode.run()

if __name__ == '__main__':
    main()