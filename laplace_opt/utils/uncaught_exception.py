# libraries
import sys
import traceback

from laplace_log import log


def log_uncaught_exceptions(exctype, value, tb):
    log.error("Uncaught exception occurred")
    log.error("".join(traceback.format_exception(exctype, value, tb)))

sys.excepthook = log_uncaught_exceptions