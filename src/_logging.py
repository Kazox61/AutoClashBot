from core import instance
import logging
import server
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


class WebSocketHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record: logging.LogRecord):
        try:
            thread_name = instance.thread_storage.name
        except AttributeError:
            thread_name = "main"
        message = {
            "type": "logging",
            "thread": thread_name,
            "log_type": record.levelname,
            "message": record.message
        }
        server.broadcast_message(message)


def setup_logger(name, log_file, level):
    """To setup as many loggers as you want"""

    stream_handler = logging.StreamHandler()  # this handler will log to stderr
    file_handler = logging.FileHandler(
        filename=log_file, encoding='utf-8', mode='w')
    ws_handler = WebSocketHandler()
    handlers = [stream_handler, file_handler, ws_handler]

    logger = logging.getLogger(name)
    logger.setLevel(level)
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
