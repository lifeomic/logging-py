# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to
[Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2024-10-11

### Added

- Added a new `JsonLogger` class that logs messages in JSON format. Supports
  child loggers as well. The logger inherits from builtin `logging.Logger` and
  the log methods have the same API as the builtin as well. Example usage:

  ```python
  from lifeomic_logging import JsonLogger

  # Create a logger with a name and optional context that will be included
  # on all log messages.
  logger = JsonLogger("my-logger", {"foo": "bar"})
  logger.info({"msg": "message", "isTrue": True})
  # >>> {"name": "my-logger", "foo": "bar", "level": "INFO", "msg": "message", "isTrue": true}
  child_logger = logger.child({"fizz": "buzz"})
  child.info("message")
  # >>> {"name": "my-logger", "foo": "bar", "fizz": "buzz", "level": "INFO", "msg": "message"}
  ```
