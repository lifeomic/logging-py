import unittest
from lifeomic_logging import get_request_context


class Context:
    def __init__(self, client_context):
        self.client_context = self.ClientContext(client_context)

    class ClientContext:
        def __init__(self, custom):
            self.custom = custom


class EventTest(unittest.TestCase):

    def test_event(self):
        context = get_request_context(None)
        self.assertIsNone(context)

        context = get_request_context(Context({}))
        self.assertIsNone(context)

        context = get_request_context(Context({
            "lifeomic-user": "user",
            "lifeomic-account": "acc",
            "lifeomic-correlation-id": "1234",
            "lifeomic-request-id": "5678"
        }))
        self.assertDictEqual(context, {
            "account": "acc",
            "correlationId": "1234",
            "requestId": "5678",
            "user": "user"
        })
