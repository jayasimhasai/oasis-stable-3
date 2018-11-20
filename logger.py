import logging


def logger_variable(name, file_handler):

    # f = open(file_handler, 'w')
    # f.close()
    # initialize logger
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
