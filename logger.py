import logging
import sys


# By default, the logging module print the messages through the stderr output. This is not the desired behavior for
# azure analytics workspace. We want to print from ERROR level and above to stderr and everything else to stdout.

# Level 50: CRITICAL
# Level 40: ERROR
# Threshold level is 30
# Level 30: WARNING
# Level 20: INFO
# Level 10: DEBUG
# Level 0: NOTSET


class InfoFilter(logging.Filter):
    def filter(self, rec: logging.LogRecord):
        """
        Filter out all messages not of level WARNING or lower(<=30).
        """
        return rec.levelno <= logging.WARNING


# Format:
# asctime: The time at which the LogRecord was created (as returned by time.time()).
# name: The name of the logger used to log the call.
# module: The module (name portion of filename) in which the logging call was issued (if available).
# lineno: The source line number where the logging call was issued (if available).
# funcName: The function name (if available).
# levelname: The text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
# message: The logged message, computed as msg % args. This is set when Formatter.format() is invoked.

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(module)s - %(lineno)d - %(funcName)s - %(levelname)s - %("
    "message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)
logger = logging.getLogger("RestAPI_logger")
logger.setLevel(logging.DEBUG)
# handler for stdout
handler_stdout = logging.StreamHandler(sys.stdout)
handler_stdout.setLevel(logging.INFO)
handler_stdout.setFormatter(formatter)
handler_stdout.addFilter(InfoFilter())
# handler for stderr
handler_stderr = logging.StreamHandler()
handler_stderr.setLevel(logging.ERROR)
handler_stderr.setFormatter(formatter)

logger.addHandler(handler_stdout)
logger.addHandler(handler_stderr)
