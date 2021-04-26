"""
The Logging object fascilitates creation of Loguru logger objects
"""
import sys

from loguru import logger


class Logging:
    def __init__(self, config):
        self.config = config
        self.logger = logger
        self.logger.remove()

    def make_filter(self, name):
        def filter(record):
            return record["extra"].get("name") == name

        return filter

    def get_logger(self):
        self.logger.info("Getting logger...")
        if self.config["LOG_LEVEL"] not in [
            "TRACE",
            "DEBUG",
            "INFO",
            "SUCCESS",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]:
            print("------------------------------------------------------------------")
            print("")
            print(
                "Invalid log level, defaulting to INFO (Options: TRACE, DEBUG, INFO, WARNING, ERROR)"
            )
            log_level = "INFO"
            self.config["LOG_LEVEL"] = "INFO"
        else:
            log_level = self.config["LOG_LEVEL"]
        if log_level == "DEBUG":
            self.logger.add(
                sys.stderr,
                filter=self.make_filter("mainlogger"),
                format="<g>{time:DD-MM-YYYY HH:mm:ss}</> | <lvl>{level}</> \t| <c>{file}:{function}:{line}</> - <lvl>{message}</>",
                level=log_level,
            )
        elif log_level == "TRACE":
            self.logger.add(
                sys.stderr,
                filter=self.make_filter("mainlogger"),
                format="<g>{time:DD-MM-YYYY HH:mm:ss:SSSS}</> | <lvl>{level}</> \t| <c>Thread: {thread.name}</c> | <c>{file}:{function}:{line}</> - <lvl>{message}</>",
                level=log_level,
            )
        else:
            self.logger.add(
                sys.stderr,
                filter=self.make_filter("mainlogger"),
                format="<g>{time:DD-MM-YYYY HH:mm:ss}</> | <lvl>{level}</> \t| <lvl>{message}</>",
                level=log_level,
            )
        logger = self.logger.bind(name="mainlogger")
        return logger

    def get_messager(self):
        """
        Logger for messages that do not relate to the code
        """
        self.logger.add(
            sys.stderr,
            filter=self.make_filter("messagelogger"),
            format="<u><b><y>{message}</y></b></u>",
        )
        logger = self.logger.bind(name="messagelogger")
        return logger

    def log_dict(self, name: str, items_dict: dict):
        print("Printing " + name)
        longest = 0
        for key, value in items_dict.items():
            if len(key) > longest:
                longest = len(key)

        for key, value in items_dict.items():
            out = key + (longest - len(key)) * " " + " = " + str(value)
            print(out)
