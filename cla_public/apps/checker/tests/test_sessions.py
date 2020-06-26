import unittest
import uuid

from datetime import datetime
from cla_public.apps.checker.session import CheckerTaggedJSONSerializer, CheckerSessionObject, MeansTest


class TestCheckerSession(unittest.TestCase):
    def setUp(self):
        self.serializer = CheckerTaggedJSONSerializer()

    def test_checker_session_object_input(self):
        value = CheckerSessionObject()
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_means_test_input(self):
        value = MeansTest()
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_tuple_input(self):
        value = ("hello", "mate")
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_uuid_input(self):
        value = uuid.UUID
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_bytes_input(self):
        value = bytes
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_markup_input(self):
        class TestMarkup:
            markup = True

            def __call__(self):
                print("callable")

        value = TestMarkup()
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_list_input(self):
        value = ["test", "list"]
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_datetime_input(self):
        value = datetime(1990, 1, 2)
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_dict_input(self):
        value = {"test": "string"}
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_str_input(self):
        value = "hello"
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)

    def test_int_input(self):
        value = 5
        serialize = self.serializer.dumps(value)
        self.assertIsInstance(serialize, str)
