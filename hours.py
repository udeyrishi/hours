#!/usr/bin/env python3

from argparse import ArgumentParser
import csv
import os
from distutils.util import strtobool
import sys

LOG_FILE_PATH = os.path.join(os.path.expanduser('~'), '.hour_logger', 'log.csv')
WAGE_EVENT = 'WAGE_SET'

class ModeFailException(Exception):
    pass

def prompt_until_success(question, parser_fn):
    while True:
        print(question, end='')
        try:
            return parser_fn(input())
        except ValueError:
            print('Not a valid response.')

def ensure_wage(fn):
    def wrapped(*args, **kwargs):
        if os.path.isfile(LOG_FILE_PATH):
            has_wage = False
            with open(LOG_FILE_PATH, 'r') as log_file:
                csv_reader = csv.reader(log_file)
                for log in csv_reader:
                    if log[0] == WAGE_EVENT:
                        has_wage = True
                        break
            if not has_wage:
                raise ModeFailException(f'Config file at {LOG_FILE_PATH} is corrupted. Try fixing or deleting it.')
        else:
            should_configure = prompt_until_success(question=f'Looks like you have never configured {sys.argv[0]} before. Would you like to do so now? [y/n] ', parser_fn=lambda x: strtobool(x) == 1)
            if not should_configure:
                raise ModeFailException(f'{sys.argv[0]} cannot run without configuring.')

            wage = prompt_until_success(question='What is your hourly wage? ', parser_fn=float)

            if not os.path.exists(os.path.dirname(LOG_FILE_PATH)):
                os.makedirs(os.path.dirname(LOG_FILE_PATH))

            with open(LOG_FILE_PATH, 'w') as log_file:
                csv_writer = csv.writer(log_file)
                csv_writer.writerow([WAGE_EVENT, wage])

            print(f'Config log file created at: {LOG_FILE_PATH}.')

        fn(*args, **kwargs)

    return wrapped

@ensure_wage
def payment(amount):
    print(f'reached payment {amount}')

@ensure_wage
def begin():
    print('reached begin')

@ensure_wage
def end():
    print('reached end')

@ensure_wage
def status():
    print('reached status')


################################### Code for setting up the command line tool ###################################
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
    
    try:
        if matching_mode.arg_type is None:
            matching_mode.runner()
        else:
            matching_mode.runner(getattr(args, matching_mode.name))
    except ModeFailException as e:
        print(str(e))
        sys.exit(3)