import logging
from configparser import ConfigParser


def logger_variable(name, file_handler):

    logger = logging.getLogger(name)
    # setLevel -> DEBUG
    logger.setLevel(logging.DEBUG)
    # set logging formatter
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    # set the logger file handler for logging to a particular file
    file_handler = logging.FileHandler(file_handler)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def update_status(file_name, section, keys, values):

    parser = ConfigParser()
    parser.read(file_name)
    parser.set(section, keys, values)
    with open(file_name, 'w') as configfile:
        parser.write(configfile)
    configfile.close()
    return
