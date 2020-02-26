import unittest
from cla_public.app import create_app


class FlaskAppTestCase(unittest.TestCase):
    CONFIG_FILE = "config/testing.py"

    def setUp(self):
        super(FlaskAppTestCase, self).setUp()
        self.app = self.create_flask_app()
        self.context = self.app.test_request_context()
        self.context.push()

    def tearDown(self):
        self.context.pop()

    def create_flask_app(self):
        return create_app(self.CONFIG_FILE)
