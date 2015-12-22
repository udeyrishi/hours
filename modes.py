import os
import abc
import json
import time
from datetime import datetime

SETUP_DIR = '.hour_logger'
CONFIG_FILE = 'config.json'
END_LINE = '--------------------------------------------\n'

class Mode:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def run(self):
        pass

def get_mode(options):
    if options is None or len(options) < 1:
        raise ValueError('Command line options needed.')

    if (options[0] == '--config'):
        if (len(options) < 2):
            raise ValueError('No config arguments passed.')
        return ConfigMode(options[1:])

    elif (options[0] == '--start'):
        return StartMode()

    elif (options[0] == '--end'):
        return EndMode()

    else:
        raise ValueError("Unknown option: '{0}'".format(options[0]))

class Configuration:
    def is_configured(self):
        if not os.path.exists(self.get_config_file_path()):
            return False

        with open(self.get_config_file_path(), 'r') as config_file:
            try:
                json.load(config_file)
                return True
            except JSONDecodeError:
                return False

    def get_configuration(self):
        if not self.is_configured():
            raise NotYetConfiguredError('Program has not been configured yet.')

        with open(self.get_config_file_path(), 'r') as config_file:
            return json.load(config_file)

    def get_config_file_path(self):
        return os.path.join(SETUP_DIR, CONFIG_FILE)

class ConfigMode(Mode):

    def __init__(self, config):
        self.__parse_config_args(config)

    def run(self):
        super()

        os.makedirs(SETUP_DIR, exist_ok = True)

        config = Configuration()

        if (config.is_configured()):
            already_existing_config = config.get_configuration()

            settings_to_be_kept = {
                key : value
                for key, value in already_existing_config.items()
                if key not in self.__config
            }
            self.__config.update(settings_to_be_kept)


        with open(config.get_config_file_path(), 'w') as config_file:
            json.dump(self.__config, config_file, indent=4)

    def __parse_config_args(self, config_args):
        if len(config_args) % 2 is not 0:
            raise ValueError("No value for config option '{0}'".format(config_args[-1]))

        self.__config = {}
        for key, value in zip(*[iter(config_args)]*2):

            if (key[0] == '-'):
                self.__config[key[1:]] = value
            else:
                raise ValueError("Bad command line parameter: '{0}.'".format(key))

class NotYetConfiguredError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class LogMode(Mode):

    def get_logfile_path(self):
        config = Configuration().get_configuration()

        if 'logfile' not in config:
            raise NotYetConfiguredError("logfile not yet configured. Use '--config "
                                        "-logfile path/to/logfile.txt' flag to "
                                        "configure")
        return config['logfile']

    def get_lastline(self):
        logfile_path = self.get_logfile_path()

        with open(logfile_path, 'a+') as logfile:
            logfile.seek(0)
            last_line = None
            for line in logfile:
                if (line is not '\n'):
                    last_line = line

            return last_line


class StartMode(LogMode):

    def run(self):
        last_line = self.get_lastline()

        if last_line is None or last_line == END_LINE:
            logfile_path = self.get_logfile_path()
            with open(logfile_path, 'a+') as logfile:
                logfile.write('Start: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
        else:
            if last_line.startswith('Start: '):
                raise ValueError('Previous shift not ended yet.')
            else:
                raise ValueError('Log file corrupted. Last line is not recognizable.')


class EndMode(LogMode):

    def run(self):
        last_line = self.get_lastline()

        if last_line is None:
            raise ValueError('No shift time started yet.')
        elif last_line.startswith('Start: '):
            starttime = datetime.strptime(last_line.strip('Start: ').strip(), "%Y-%m-%d %H:%M:%S")
            endtime = time.strftime("%Y-%m-%d %H:%M:%S")
            duration = (datetime.strptime(endtime, "%Y-%m-%d %H:%M:%S") - starttime).seconds / 3600

            with open(self.get_logfile_path(), 'a+') as logfile:
                logfile.write('End: ' + endtime + '\n')
                logfile.write('Duration: ' + str(duration) + ' hours \n')
                config = Configuration().get_configuration()
                if 'rate' in config:
                    rate = float(config['rate'])
                    money = rate*duration
                    logfile.write('Money earned: $%.2f\n' %money)

                logfile.write(END_LINE + '\n')
        elif last_line == END_LINE:
            raise ValueError('No shift time started yet.')
        else:
            raise ValueError('Log file corrupted. Last line is not recognizable.')