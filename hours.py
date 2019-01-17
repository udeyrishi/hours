#!/usr/bin/env python3

from argparse import ArgumentParser


def payment(amount):
    print(f'reached payment {amount}')

def begin():
    print('reached begin')

def end():
    print('reached end')

def status():
    print('reached status')

class Mode:
    def __init__(self, name, runner, help, arg_type=None):
        self.name = name
        self.runner = runner
        self.arg_type = arg_type
        self.help = help

MODES = [
    Mode(name='status', runner=status, help='see the current status summary'),
    Mode(name='begin', runner=begin, help='begin a shift'),
    Mode(name='end', runner=end, help='end a shift'),
    Mode(name='payment', runner=payment, arg_type=float, help='add a received payment')
]

DEFAULT_MODE = MODES[0]

if __name__ == '__main__':
    parser = ArgumentParser(description='A tool for managing your work hours and the money you made.')
    group = parser.add_mutually_exclusive_group()

    for mode in MODES:
        if mode.arg_type is None:
            group.add_argument(f'-{mode.name[0]}', f'--{mode.name}', action='store_true', help=mode.help)
        else: 
            group.add_argument(f'-{mode.name[0]}', f'--{mode.name}', type=mode.arg_type, help=mode.help)

    args = parser.parse_args()

    matching_mode = next((mode for mode in MODES if not not getattr(args, mode.name)), DEFAULT_MODE)
    
    if matching_mode.arg_type is None:
        matching_mode.runner()
    else:
        matching_mode.runner(getattr(args, matching_mode.name))