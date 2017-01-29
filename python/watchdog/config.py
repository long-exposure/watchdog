# Watchdog - Building supervision with Raspberry Pi
# (C)2017 - Norbert Huffschmid

# watchdog configuration functions

import ConfigParser
import logging
from threading import Lock

logger = logging.getLogger(__file__)

lock = Lock()

CONFIG_FILE = '/etc/watchdog.conf'


def has_option(section, option):
    '''Check if option exists in config file.
    @param section Section
    @param option Option name
    @return: True if option exists and False otherwise'''
    logger.debug('Check if option \'%s\' exists in section \'%s\' ...' % (option, section))
    config = ConfigParser.SafeConfigParser()
    with lock:
        config.read(CONFIG_FILE)
        if (config.has_option(section, option)):
            logger.debug('Option exists')
            return True
        else:
            logger.debug('Option does not exist')
            return False


def remove_option(section, option):
    '''Remove option from section.
    @param section Section
    @param option Option name'''
    logger.debug('Remove option \'%s\' from section \'%s\' ...' % (option, section))
    config = ConfigParser.SafeConfigParser()
    with lock:
        config.read(CONFIG_FILE)
        config.remove_option(section, option)
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)
        logger.debug('Option removed')


def get_option(section, option):
    '''Gets a config option from config file.
    @param section Section
    @param option Option name
    @return: Configuration option string'''
    logger.debug('Get option \'%s\' in section \'%s\' ...' % (option, section))
    config = ConfigParser.SafeConfigParser()
    with lock:
        config.read(CONFIG_FILE)
        result = config.get(section, option)
        logger.debug('Option value: ' + result)
        return result


def write_option(section, option, value):
    '''Writes a config option to the config file.
    @param section Section
    @param option Option name
    @param value Option value'''
    logger.debug('Write option \'%s\' with value \'%s\' in section \'%s\' ...' % (option, value, section))
    config = ConfigParser.SafeConfigParser()
    with lock:
        config.read(CONFIG_FILE)
        config.set(section, option, value)
        with open(CONFIG_FILE, 'wb') as configfile:
            config.write(configfile)
        logger.debug('Option written')
