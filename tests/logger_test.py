import unittest
import unittest.mock
import sys
import io
from datetime import datetime
import json
from lifeomic_logging import scoped_logger
from lifeomic_logging.logger import JsonLogger


class LoggerTest(unittest.TestCase):
    def setUp(self):
        stderr_patcher = unittest.mock.patch("sys.stderr", new_callable=io.StringIO)
        self.addCleanup(stderr_patcher.stop)
        self.mock_stderr = stderr_patcher.start()

        datetime_patcher = unittest.mock.patch("lifeomic_logging.logger.datetime")
        self.addCleanup(datetime_patcher.stop)
        self.mock_dt = datetime_patcher.start()
        self.mock_dt.utcnow.return_value = datetime(1901, 12, 21)

        socket_patcher = unittest.mock.patch("lifeomic_logging.logger.socket")
        self.addCleanup(socket_patcher.stop)
        self.mock_socket = socket_patcher.start()
        self.mock_socket.gethostname.return_value = "hostname"

        os_patcher = unittest.mock.patch("lifeomic_logging.logger.os")
        self.addCleanup(os_patcher.stop)
        self.os_patcher = os_patcher.start()
        self.os_patcher.getpid.return_value = 1

        self.maxDiff = 1500

    def test_info(self):
        with scoped_logger("test_info", stream=sys.stderr) as logger:
            logger.info("message")

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 30,
                "msg": "message",
                "name": "test_info",
                "pid": 1,
                "severity": "INFO",
                "time": "1901-12-21T00:00:00",
            },
        )

    def test_warn(self):
        with scoped_logger("test_warning", stream=sys.stderr) as logger:
            logger.warning("message")

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 40,
                "msg": "message",
                "name": "test_warning",
                "pid": 1,
                "severity": "WARNING",
                "time": "1901-12-21T00:00:00",
            },
        )

    def test_error(self):
        with scoped_logger("test_error", stream=sys.stderr) as logger:
            logger.error("message")

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 50,
                "msg": "message",
                "name": "test_error",
                "pid": 1,
                "severity": "ERROR",
                "time": "1901-12-21T00:00:00",
            },
        )

    def test_exception(self):
        with scoped_logger("test_exception", stream=sys.stderr) as logger:
            try:
                raise TypeError("error message")
            except Exception as e:
                logger.exception("Unknown Error")

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertEquals(parsed.get("severity"), "ERROR")
        self.assertEquals(parsed.get("msg"), "Unknown Error")
        self.assertIsNotNone(parsed.get("err").get("message"))

    def test_extra(self):
        with scoped_logger("test_extra", stream=sys.stderr) as logger:
            logger.info("message", extra={"bar": "baz"})

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 30,
                "msg": "message",
                "name": "test_extra",
                "pid": 1,
                "severity": "INFO",
                "time": "1901-12-21T00:00:00",
                "bar": "baz",
            },
        )

    def test_dict(self):
        with scoped_logger("test_dict", stream=sys.stderr) as logger:
            logger.info({"bar": "baz"})

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 30,
                "name": "test_dict",
                "pid": 1,
                "severity": "INFO",
                "time": "1901-12-21T00:00:00",
                "bar": "baz",
            },
        )

    def test_normal_context(self):
        with scoped_logger(
            "test_normal_context",
            normal_context={"account": "foo"},
            error_context={"error": True},
            stream=sys.stderr,
        ) as logger:
            logger.info("message")

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 30,
                "msg": "message",
                "name": "test_normal_context",
                "pid": 1,
                "severity": "INFO",
                "time": "1901-12-21T00:00:00",
                "account": "foo",
            },
        )

    def test_error_context(self):
        with scoped_logger(
            "test_error_context",
            normal_context={"account": "foo"},
            error_context={"error": True},
            stream=sys.stderr,
        ) as logger:
            logger.error("message")

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 50,
                "msg": "message",
                "name": "test_error_context",
                "pid": 1,
                "severity": "ERROR",
                "time": "1901-12-21T00:00:00",
                "account": "foo",
                "error": True,
            },
        )

    def test_info_with_args(self):
        with scoped_logger("test_info_with_args", stream=sys.stderr) as logger:
            logger.info("message %s %d", "foo", 1)

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 30,
                "msg": "message foo 1",
                "name": "test_info_with_args",
                "pid": 1,
                "severity": "INFO",
                "time": "1901-12-21T00:00:00",
            },
        )

    def test_info_with_no_args(self):
        with scoped_logger("test_info_with_no_args", stream=sys.stderr) as logger:
            # Since no string format arguments are provided, the logger should treat
            # `%s` and `%d` as literal values, not string placeholders.
            logger.info("message %s %d")

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 30,
                "msg": "message %s %d",
                "name": "test_info_with_no_args",
                "pid": 1,
                "severity": "INFO",
                "time": "1901-12-21T00:00:00",
            },
        )

    def test_json_logger_will_log_additional_context_using_child(self):
        logger = JsonLogger("test-logger", {"parentContext": True})
        child_logger = logger.child({"childContext": True})
        child_logger.info("message")
        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertDictEqual(
            parsed,
            {
                "hostname": "hostname",
                "level": 30,
                "msg": "message",
                "name": "test-logger",
                "pid": 1,
                "severity": "INFO",
                "time": "1901-12-21T00:00:00",
                "parentContext": True,
                "childContext": True,
            },
        )

    def test_json_logger_exception_includes_error(self):
        logger = JsonLogger("test-logger", {"parentContext": True})
        try:
            raise TypeError("error message")
        except Exception:
            logger.exception("Unknown Error")

        parsed = json.loads(self.mock_stderr.getvalue())
        self.assertEquals(parsed["severity"], "ERROR")
        self.assertEquals(parsed["msg"], "Unknown Error")
        self.assertIsNotNone(parsed["err"].get("message"))
        self.assertEquals(parsed["parentContext"], True)
