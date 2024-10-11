import socket
import os
from datetime import datetime
import threading
import uuid
from collections import OrderedDict
from logging import Formatter, Filter, StreamHandler, getLogger, INFO, Logger
from json import dumps
from contextlib import contextmanager
from typing import Generator, Optional

thread_local_storage = threading.local()

_RESERVED_ATTRS = (
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
)


class JsonLogger(Logger):
    """
    A logger that logs in JSON format. Supports creating child loggers with
    expanded context, similar to the NodeJS Bunyan logger.
    """

    def __init__(
        self,
        name: str,
        context: Optional[dict] = None,
        level: int = INFO,
    ):
        super().__init__(name, level)
        self.context = context if context is not None else {}
        handler = StreamHandler()
        handler.setFormatter(_JSONFormatter())
        self.addHandler(handler)

    def child(self, additional_context: dict):
        child_context = {**self.context, **additional_context}
        child_logger = self.__class__(
            name=self.name, level=self.level, context=child_context
        )
        return child_logger

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False):
        if extra is None:
            extra = {}
        extra.update(self.context)
        super()._log(level, msg, args, exc_info, extra, stack_info)


@contextmanager
def scoped_logger(
    logname: str,
    normal_context: Optional[dict] = None,
    error_context: Optional[dict] = None,
    stream=None,
    level: int = INFO,
) -> Generator[Logger, None, None]:
    """Creates a scopped logger

    Parameters
    ----------
    logname : str
        The name of the logger
    normal_context : dict, optional
        Dict of values to add to the logger, by default None
    error_context : dict, optional
        Dict of values to add to the logger when an error occurs,
        by default None
    stream : Stream, optional
        A stream to send the log events to, by default None
    level : int, optional
        The logging level, by default INFO

    Returns
    -------
    logging.Logger
        The scoped logger
    """

    try:
        _LoggingContextFilter.push_context(
            normal_context, _LoggingContextFilter.tls_normal_context_field_name
        )
        _LoggingContextFilter.push_context(
            error_context, _LoggingContextFilter.tls_error_context_field_name
        )

        yield _logger(logname, StreamHandler(stream), level)
    finally:
        _LoggingContextFilter.pop_context(
            _LoggingContextFilter.tls_normal_context_field_name
        )
        _LoggingContextFilter.pop_context(
            _LoggingContextFilter.tls_error_context_field_name
        )


def get_request_context(lambda_context: dict) -> Optional[dict]:
    """Helper method to retrieve our most pertinent header information.
        These are stored from the passed in lambda_context
        object. Please see
        https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
        for the structure.

    Parameters
    ----------
    lambda_context : dict
        The lambda context

    Returns
    -------
    dict
        A dict of important properties for the request
    """
    if not lambda_context:
        return None

    client_context = getattr(lambda_context, "client_context", None)
    if not client_context:
        return None

    custom = getattr(client_context, "custom", None)
    if not custom:
        return None

    request_user = custom.get("lifeomic-user", "(unknown user)")
    request_account = custom.get("lifeomic-account", "(unknown account)")
    request_correlation_id = custom.get("lifeomic-correlation-id", str(uuid.uuid4()))
    request_id = custom.get("lifeomic-request-id", request_correlation_id)

    return {
        "account": request_account,
        "correlationId": request_correlation_id,
        "requestId": request_id,
        "user": request_user,
    }


def _logger(name: str, handler, level: int = INFO) -> Logger:
    log = getLogger(name)

    if not log.handlers:
        textformatter = _JSONFormatter()
        handler.setFormatter(textformatter)
        log.addHandler(handler)

    if not log.filters:
        log.addFilter(_LoggingContextFilter())

    log.setLevel(level)
    log.propagate = False

    return log


class _LoggingContextFilter(Filter):
    logger_context_field_name = "context"
    tls_normal_context_field_name = "normal_request_context"
    tls_error_context_field_name = "error_request_context"

    def __init__(self):
        super(_LoggingContextFilter, self).__init__()

    def filter(self, record):
        normal_request_context = _LoggingContextFilter.merge_context(
            self.tls_normal_context_field_name
        )
        error_request_context = _LoggingContextFilter.merge_context(
            self.tls_error_context_field_name
        )

        log_context = normal_request_context.copy()
        if record.levelname != "INFO":
            log_context.update(error_request_context)

        [log_context.pop(key, None) for key in _RESERVED_ATTRS]
        record.__dict__.update(log_context)

        return True

    @staticmethod
    def push_context(context, context_name):
        existing_context = getattr(thread_local_storage, context_name, [])
        existing_context.append(context if context else {})
        setattr(thread_local_storage, context_name, existing_context)

    @staticmethod
    def merge_context(context_name):
        contexts = getattr(thread_local_storage, context_name, None)
        if contexts is None:
            return {}
        merged_context = {}
        for context in contexts:
            merged_context.update(context)
        return merged_context

    @staticmethod
    def pop_context(context_name):
        existing_context = getattr(thread_local_storage, context_name, [])
        if len(existing_context) > 0:
            existing_context.pop()


class _JSONFormatter(Formatter):
    def _getjsondata(self, record):
        fields = []
        fields.append(("name", record.name))
        if isinstance(record.msg, dict):
            for key, value in record.msg.items():
                fields.append((key, value))
        else:
            msg = str(record.msg)
            if len(record.args) > 0:
                msg = msg % record.args
            fields.append(("msg", msg))

        fields.append(("severity", record.levelname))
        # Python logging levels are 10 less than what Bunyan uses
        fields.append(("level", record.levelno + 10))
        fields.append(("time", datetime.utcnow().isoformat()))

        if record.exc_info:
            fields.append(
                (
                    "err",
                    {
                        "message": self.formatException(record.exc_info),
                        "stack": self.formatStack(record.stack_info)
                        if record.stack_info
                        else None,
                    },
                )
            )

        fields.append(("hostname", socket.gethostname()))
        fields.append(("pid", os.getpid()))

        for key, value in record.__dict__.items():
            if key not in _RESERVED_ATTRS and not (
                hasattr(key, "startswith") and key.startswith("_")
            ):
                fields.append((key, value))

        return OrderedDict(fields)

    def format(self, record):
        jsondata = self._getjsondata(record)
        formattedjson = dumps(jsondata)
        return formattedjson
