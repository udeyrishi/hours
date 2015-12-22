import os
import abc
import json

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

    if (options[0] == '-config'):
        if (len(options) < 2):
            raise ValueError('Logfile path needed as second argument.')
        return ConfigMode(options[1])

    elif (options[0] == '-start'):
        return None

    elif (options[0] == '-end'):
        return None

    else:
        raise ValueError("Unknown option: '{0}'".format(options[0]))

class ConfigMode(Mode):

    def __init__(self, logfile):
        self._logfile = logfile

    def run(self):
        super()
        os.makedirs(SETUP_DIR, exist_ok = True)
        config = { 'logfile': self._logfile }
        with open(os.path.join(SETUP_DIR, CONFIG_FILE), 'w') as config_file:
            json.dump(config, config_file, indent=4)