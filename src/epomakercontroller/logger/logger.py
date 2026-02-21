from __future__ import annotations

import enum


class LogScope(enum.StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Logger:
    @staticmethod
    def log(scope: LogScope, message: str):
        # TODO: Refactor to logging library w/ custom format + file writing
        # pylint: disable=bad-builtin
        print(f"{scope.value}: {message}")

    @staticmethod
    def log_info(message: str):
        Logger.log(LogScope.INFO, message)

    @staticmethod
    def log_warning(message: str):
        Logger.log(LogScope.WARNING, message)

    @staticmethod
    def log_error(message: str):
        Logger.log(LogScope.ERROR, message)
