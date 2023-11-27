from enum import Enum
from datetime import datetime
import os
from colored import Fore, Style


class LogPriority(Enum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4


class Logger:
    _print_to_console: bool = True
    _write_to_file: bool = True
    _current_log_priority = LogPriority.DEBUG
    _file_path = os.path.join(__file__, "../../logs")
    _file_name = "log.txt"

    @classmethod
    def init(cls):
        if not os.path.exists(cls._file_path):
            os.makedirs(cls._file_path, exist_ok=True)

    @classmethod
    def debug(cls, message: str):
        cls._log(LogPriority.DEBUG, "[Debug]",
                 message, Fore.RGB(155, 155, 155))

    @classmethod
    def info(cls, message: str):
        cls._log(LogPriority.INFO, "[Info]", message, Fore.RGB(130, 199, 250))

    @classmethod
    def warn(cls, message: str):
        cls._log(LogPriority.WARN, "[Warn]", message, Fore.RGB(255, 165, 0))

    @classmethod
    def error(cls, message: str):
        cls._log(LogPriority.ERROR, "[Error]", message, Fore.RGB(255, 0, 0))

    @classmethod
    def _log(cls, log_priority: LogPriority, message_prefix: str, message: str, color):
        if log_priority.value < cls._current_log_priority.value:
            return
        current_time = datetime.now()
        text = f"{current_time} {message_prefix} {message}"
        if cls._print_to_console:
            print(f"{color} {text} {Style.reset}")

        if cls._write_to_file:
            f = open(os.path.join(cls._file_path, cls._file_name), "a")
            f.write(text + "\n")
            f.close()
