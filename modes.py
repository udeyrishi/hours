import os
import abc
import json
import time
from datetime import datetime

SETUP_DIR = '/usr/local/bin/hours_data'
CONFIG_FILE = 'config.json'
END_LINE = '--------------------------------------------'


class Mode:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self):
        pass


def get_mode(options):
    if options is None or len(options) < 1:
        raise ValueError('Command line options needed.')

    if options[0] == '--config':
        if len(options) < 2:
            raise ValueError('No config arguments passed.')
        return ConfigMode(options[1:])

    elif options[0] == '--start':
        return StartMode()

    elif options[0] == '--end':
        return EndMode()

    elif options[0] == '--payment':
        if len(options) < 2:
            raise ValueError('Payment amount needed as argument.')

        return PaymentMode(options[1])

    else:
        raise ValueError("Unknown option: '{0}'".format(options[0]))


def get_config_file_path():
    return os.path.join(SETUP_DIR, CONFIG_FILE)


def is_configured():
    if not os.path.exists(get_config_file_path()):
        return False

    with open(get_config_file_path(), 'r') as config_file:
        try:
            json.load(config_file)
            return True
        except json.decoder.JSONDecodeError:
            return False


def get_configuration():
    if not is_configured():
        raise NotYetConfiguredError('Program has not been configured yet.')

    with open(get_config_file_path(), 'r') as config_file:
        return json.load(config_file)


def get_logfile_path():
    config = get_configuration()

    if 'logfile' not in config:
        raise NotYetConfiguredError("logfile not yet configured. Use '--config "
                                    "-logfile path/to/logfile.txt' flag to "
                                    "configure")
    return config['logfile']


def get_wage_rate():
    config = get_configuration()

    if 'rate' not in config:
        raise NotYetConfiguredError('Please configure the earning hourly wage. e.g.: --config -rate 13.45')

    return float(config['rate'])


def get_last_non_payment_line():
    logfile_path = get_logfile_path()

    with open(logfile_path, 'a+') as logfile:
        logfile.seek(0)
        last_line = None
        for line in logfile:
            if line is not '\n' and not line.startswith('Payment'):
                last_line = line

        return last_line.strip()


def get_duration_hours(start, end):
    delta = (end - start)
    return (delta.days * 24) + (delta.seconds / 3600)


def parse_time(time_string, initial_keyword):
    return datetime.strptime(time_string.strip(initial_keyword).strip(), "%Y-%m-%d %H:%M:%S")


class NotYetConfiguredError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConfigMode(Mode):
    def __init__(self, config):
        self.__parse_config_args(config)

    def run(self):
        super()

        os.makedirs(SETUP_DIR, exist_ok=True)

        if is_configured():
            already_existing_config = get_configuration()

            settings_to_be_kept = {
                key: value
                for key, value in already_existing_config.items()
                if key not in self.__config
                }
            self.__config.update(settings_to_be_kept)

        with open(get_config_file_path(), 'w') as config_file:
            json.dump(self.__config, config_file, indent=4)

    def __parse_config_args(self, config_args):
        if len(config_args) % 2 is not 0:
            raise ValueError("No value for config option '{0}'".format(config_args[-1]))

        self.__config = {}
        for key, value in zip(*[iter(config_args)] * 2):

            if key[0] == '-':
                self.__config[key[1:]] = value
            else:
                raise ValueError("Bad command line parameter: '{0}.'".format(key))


class StartMode(Mode):
    def run(self):
        last_line = get_last_non_payment_line()

        if last_line is None or last_line == END_LINE:
            logfile_path = get_logfile_path()
            with open(logfile_path, 'a+') as logfile:
                logfile.write('Start: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
        else:
            if last_line.startswith('Start: '):
                raise ValueError('Previous shift not ended yet.')
            else:
                raise ValueError('Log file corrupted. Last line is not recognizable.')


class EndMode(Mode):
    def run(self):
        last_line = get_last_non_payment_line()

        if last_line is None:
            raise ValueError('No shift time started yet.')
        elif last_line.startswith('Start: '):
            start_time = parse_time(last_line, 'Start: ')
            end_time = time.strftime("%Y-%m-%d %H:%M:%S")

            duration = get_duration_hours(start_time, parse_time(end_time, ' '))

            with open(get_logfile_path(), 'a+') as logfile:
                logfile.write('End: ' + end_time + '\n')
                logfile.write('Duration: ' + "%.4f" % duration + ' hours \n')
                config = get_configuration()
                if 'rate' in config:
                    rate = float(config['rate'])
                    money = rate * duration
                    logfile.write('Money earned: $%.2f\n' % money)

                logfile.write(END_LINE + '\n')
        elif last_line == END_LINE:
            raise ValueError('No shift time started yet.')
        else:
            raise ValueError('Log file corrupted. Last line is not recognizable.')


class PaymentMode(Mode):
    def __init__(self, payment):
        self.__payment = float(payment)

    def run(self):
        pending_payment = self.__get_pending_payment()

        logfile_path = get_logfile_path()
        with open(logfile_path, 'a+') as logfile:
            logfile.write('Payment Made: {0:s} : ${1:.2f}\n'.format(time.strftime("%Y-%m-%d %H:%M:%S"), self.__payment))
            logfile.write('Payment Pending: $%.2f\n' % (pending_payment - self.__payment))

    @staticmethod
    def __get_pending_payment():
        rate = get_wage_rate()
        logfile_path = get_logfile_path()

        pending_payment = 0

        if not os.path.isfile(logfile_path):
            return 0

        with open(logfile_path, 'r') as logfile:
            last_start = None

            for line in logfile.readlines():
                if line.startswith('Start: '):
                    if last_start is None:
                        last_start = parse_time(line, 'Start: ')
                    else:
                        raise ValueError("Logfile corrupted. Two successive 'Start' statements without an 'End' one.")
                elif line.startswith('End: '):
                    if last_start is None:
                        raise ValueError("Logfile corrupted. Two successive 'End' statements without a 'Start' one.")
                    else:
                        end_time = parse_time(line, 'End: ')
                        duration = get_duration_hours(last_start, end_time)
                        last_start = None
                        pending_payment += rate * duration
                elif line.startswith('Payment Made: '):
                    payment_made = float(line[line.rfind('$') + 1:])
                    pending_payment -= payment_made

        return pending_payment
