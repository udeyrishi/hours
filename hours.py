#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError
import csv
import datetime
from enum import Enum, auto
import os
from distutils.util import strtobool
from math import isclose
import sys
import time

LOG_FILE_PATH = os.path.join(os.path.expanduser('~'), '.hour_logger', 'log.csv')

class ModeFailException(Exception):
    pass

def prompt_until_success(question, parser_fn):
    while True:
        print(question, end='')
        try:
            return parser_fn(input())
        except ValueError:
            print('Not a valid response.')

class LogEvent(Enum):
    WAGE_SET = auto()
    PAYMENT = auto()
    BEGIN = auto()
    END = auto()

class LogReport:
    def __init__(self, active_wage=None, current_shift_started_at=None, total_earned=0, total_paid=0):
        self.active_wage = active_wage
        self.current_shift_started_at = current_shift_started_at
        self.total_earned = total_earned
        self.total_paid = total_paid

    @property
    def outstanding_payment(self):
        return self.total_earned - self.total_paid

    @property
    def has_outstanding_payment(self):
        return not isclose(self.total_earned, self.total_paid, abs_tol=0.01)

    @property
    def in_shift(self):
        return self.current_shift_started_at != None

    @property
    def has_active_wage(self):
        return self.active_wage != None

    @property
    def current_shift_duration(self):
        if self.current_shift_started_at is None:
            return None
        else:
            duration = time.time() - self.current_shift_started_at
            if duration < 0:
                raise ModeFailException(f'Log file at {LOG_FILE_PATH} is corrupted; the ongoing shift seems to have been started in the future.')
            return duration

def prepare_report():
    report = LogReport()
    
    for event, value in read_log():
        if event == LogEvent.WAGE_SET:
            report.active_wage = value
        elif event == LogEvent.PAYMENT:
            report.total_paid += value
        elif event == LogEvent.BEGIN: 
            if report.in_shift:
                raise ModeFailException(f'Log file at {LOG_FILE_PATH} is corrupted; found two successive {LogEvent.BEGIN.name}s without a {LogEvent.END.name} in between. Try fixing or deleting it.')
            if report.active_wage is None:
                raise ModeFailException(f'Log file at {LOG_FILE_PATH} is corrupted; A shift {event.name} event occurred before any {LogEvent.WAGE_SET.name} event.')
            report.current_shift_started_at = value
        elif event == LogEvent.END:
            if not report.in_shift:
                raise ModeFailException(f'Log file at {LOG_FILE_PATH} is corrupted; found two successive {LogEvent.END.name}s without a {LogEvent.BEGIN.name} in between. Try fixing or deleting it.')
            if report.active_wage is None:
                raise ModeFailException(f'Log file at {LOG_FILE_PATH} is corrupted; A shift {event.name} event occurred before any {LogEvent.WAGE_SET.name} event.')
            
            seconds = value - report.current_shift_started_at
            report.current_shift_started_at = None
            if (seconds < 0):
                raise ModeFailException(f'Log file at {LOG_FILE_PATH} is corrupted; A shift\'s duration cannot be negative. Try fixing or deleting it.')
            
            report.total_earned += (seconds/60/60) * report.active_wage
        else:
            assert False, f'Support for new LogEvent {event.name} not added.'

    return report


def read_log():
    with open(LOG_FILE_PATH, 'r') as log_file:
        csv_reader = csv.reader(log_file)
        for log in csv_reader:
            event = next((e for e in LogEvent if e.name == log[0]), None)
            if event is None:
                raise ModeFailException(f'Log file at {LOG_FILE_PATH} is corrupted; found an unknown log event: {log}')
            value = float(log[1])
            yield event, value

def write_log(event, value):
    with open(LOG_FILE_PATH, 'a') as log_file:
        csv_writer = csv.writer(log_file)
        csv_writer.writerow([event.name, value])

def read_sanitized_report(expected_in_shift=None, failure_msg=None):
    if (expected_in_shift is None and failure_msg is not None) or (expected_in_shift is not None and failure_msg is None):
        raise ValueError('Either both, or neither of expected_in_shift and failure_msg should be null.')

    report = prepare_report()
    if not report.has_active_wage:
        raise ModeFailException(f'Log file at {LOG_FILE_PATH} is corrupted; no {LogEvent.WAGE_SET.name} events found. Try fixing or deleting it.')

    if expected_in_shift is not None and report.in_shift != expected_in_shift:
        raise ModeFailException(failure_msg)

    return report

def configure_as_new():
    should_configure = prompt_until_success(question=f'Looks like you have never configured {sys.argv[0]} before. Would you like to do so now? [y/n] ', parser_fn=lambda x: strtobool(x) == 1)
    if not should_configure:
        raise ModeFailException(f'{sys.argv[0]} cannot run without configuring.')

    wage = prompt_until_success(question='What is your hourly wage? ', parser_fn=float)

    if not os.path.exists(os.path.dirname(LOG_FILE_PATH)):
        os.makedirs(os.path.dirname(LOG_FILE_PATH))

    write_log(LogEvent.WAGE_SET, wage)

    print(f'Log log file created at: {LOG_FILE_PATH}.')

    return LogReport(active_wage=wage)

class Mode:
    def __init__(self, name, runner, help, arg_type=None):
        self.name = name
        self.runner = runner
        self.arg_type = arg_type
        self.help = help

def positive_float(val):
    num = float(val)
    if num < 0:
        raise ArgumentTypeError(f'{val} is a negative number.')
    return num

MODES = []

def mode(expected_in_shift=None, failure_msg=None, help=None):
    class ModeParamData:
        def __init__(self, index, name, type):
            self.index = index
            self.name = name
            self.type = type

    def _ensure_integrity(fn):
        assert len(fn.__annotations__) <= 2, 'mode functions can only either accept 1 command line arg, the current log report, or both.'
        
        report_param_data = next((ModeParamData(index=i, name=param[0], type=param[1]) for i, param in enumerate(fn.__annotations__.items()) if param[1] == LogReport), None)
        cli_param_data = next((ModeParamData(index=i, name=param[0], type=param[1]) for i, param in enumerate(fn.__annotations__.items()) if param[1] != LogReport), None)

        def wrapper(*args):
            if os.path.isfile(LOG_FILE_PATH):
                report = read_sanitized_report(expected_in_shift, failure_msg)
            else:
                report = configure_as_new()

            kwargs = dict()
            if cli_param_data is not None:
                kwargs[cli_param_data.name] = args[0]

            if report_param_data is not None:
                kwargs[report_param_data.name] = report
            
            fn(**kwargs)

        MODES.append(Mode(name=fn.__name__, runner=wrapper, help=help, arg_type=cli_param_data.type if cli_param_data is not None else None))
        return wrapper
    return _ensure_integrity

@mode(expected_in_shift=False, failure_msg='Cannot change the wage while a shift is ongoing.', help='update the hourly wage moving forward; must be non-negative')
def wage(wage: positive_float):
    write_log(LogEvent.WAGE_SET, wage)

@mode(help='add a received payment; must be non-negative')
def payment(amount: positive_float):
    write_log(LogEvent.PAYMENT, amount)

@mode(expected_in_shift=False, failure_msg='Cannot begin a shift while one is ongoing.', help='begin a shift')
def begin():
    write_log(LogEvent.BEGIN, time.time())

@mode(expected_in_shift=True, failure_msg='Cannot end a shift when none is ongoing.', help='end a shift')
def end():
    write_log(LogEvent.END, time.time())

@mode(help='see the current status summary')
def status(report: LogReport):
    if report.in_shift:
        print(f'🕒 {datetime.timedelta(seconds=report.current_shift_duration)}')
    else:
        print('🏠')
    
    if report.has_outstanding_payment:
        print('---')
        if report.outstanding_payment > 0:
            print('💰 %.2f pending' % report.outstanding_payment)
        else:
            print('💰 %.2f overpaid' % -report.outstanding_payment)

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