import os
import abc
import json
import time

SETUP_DIR = '.hour_logger'
CONFIG_FILE = 'config.json'

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
        return None

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

class StartMode(Mode):

    def run(self):
        config = Configuration().get_configuration()

        if 'logfile' not in config:
            raise NotYetConfiguredError("logfile not yet configured. Use '--config "
                                        "-logfile path/to/logfile.txt' flag to "
                                        "configure")

        logfile_path = config['logfile']

        with open(logfile_path, 'a+') as logfile:
            logfile.write('Shift started at: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')

