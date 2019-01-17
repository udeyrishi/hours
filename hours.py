#!/usr/bin/env python3

from argparse import ArgumentParser
import json
from pathlib import Path
import os
from distutils.util import strtobool
import sys

CONFIG_FILE_PATH = os.path.join(Path.home(), '.hour_logger', 'config.json')

class ModeFailException(Exception):
    pass

def script_name():
    return sys.argv[0]

def prompt_until_success(question, parser_fn, default=None):
    while True:
        print(question, end='')
        try:
            return parser_fn(input())
        except ValueError:
            if default is not None:
                return default
            else:
                print('Not a valid response.')

def query_yes_no(question, default=True):
    prompt = f" [{'Y' if default else 'y'}/{'n' if default else 'N'}] "
    return prompt_until_success(question=question + prompt, parser_fn=lambda x: strtobool(x) == 1, default=default)

def new_config(file_path):
    config = {'wage': prompt_until_success(question='What is your hourly wage? ', parser_fn=float)}

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with open(file_path, 'w') as config_file:
        json.dump(config, config_file)

def needs_config(fn):
    def wrapped(*args, **kwargs):
        if not os.path.isfile(CONFIG_FILE_PATH):
            should_configure = query_yes_no(f"Looks like you've never configured {script_name()} before. Would you like to do so now?")
            if not should_configure:
                raise ModeFailException(f'{script_name()} cannot run without configuring.')

            new_config(CONFIG_FILE_PATH)
            print(f'Config file saved at: {CONFIG_FILE_PATH}.')

        fn(*args, **kwargs)

    return wrapped

@needs_config
def payment(amount):
    print(f'reached payment {amount}')

@needs_config
def begin():
    print('reached begin')

@needs_config
def end():
    print('reached end')

@needs_config
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