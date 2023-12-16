import logging

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


def setup_logger(name, log_file, webhook_url, level):
    """To setup as many loggers as you want"""

    stream_handler = logging.StreamHandler()  # this handler will log to stderr
    file_handler = logging.FileHandler(
        filename=log_file, encoding='utf-8', mode='w')
    handlers = [stream_handler, file_handler]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
