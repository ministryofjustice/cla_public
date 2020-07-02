import unittest
import uuid
from flask import json
from base64 import b64encode
from flask._compat import text_type
from werkzeug.http import http_date
from datetime import datetime
from cla_public.apps.checker.session import CheckerTaggedJSONSerializer, CheckerSessionObject, MeansTest


class TestCheckerSession(unittest.TestCase):
    def setUp(self):
        self.serializer = CheckerTaggedJSONSerializer()

    def assert_json(self, value):
        try:
            json.loads(value)
        except Exception:
            self.fail("Not valid JSON")

    def format_json(self, value):
        return json.dumps(value, separators=(",", ":"))

    def compare_dicts(self, outputDict, expectedDict):
        for key, value in expectedDict.items():
            if isinstance(value, dict):
                self.compare_dicts(outputDict[key], value)
            else:
                self.assertEqual(outputDict[key], value)

    def test_serializer_with_checker_session_object(self):
        value = CheckerSessionObject({"checker": {"foo": "bar"}})
        outputJSON = self.serializer.dumps(value)
        expectedDict = {" ch": {"checker": {"foo": {" b": b64encode("bar").decode("ascii")}}}}
        expectedJSON = self.format_json(expectedDict)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)

    def test_serializer_with_means_test(self):
        value = MeansTest()
        outputJSON = self.serializer.dumps(value)
        expectedDict = {
            u" mt": {
                u"on_passported_benefits": {u" b": b64encode("0").decode("ascii")},
                u"specific_benefits": {},
                u"dependants_old": 0,
                u"you": {
                    u"savings": {
                        u"credit_balance": 0,
                        u"investment_balance": 0,
                        u"asset_balance": 0,
                        u"bank_balance": 0,
                    },
                    u"deductions": {
                        u"income_tax": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"mortgage": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"childcare": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"rent": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"maintenance": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"criminal_legalaid_contributions": 0,
                        u"national_insurance": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                    },
                    u"income": {
                        u"self_employment_drawings": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"benefits": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"maintenance_received": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"self_employed": {u" b": b64encode("0").decode("ascii")},
                        u"tax_credits": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"earnings": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"child_benefits": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"other_income": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                        u"pension": {
                            u"per_interval_value": 0,
                            u"interval_period": {u" b": b64encode("per_month").decode("ascii")},
                        },
                    },
                },
                u"dependants_young": 0,
                u"on_nass_benefits": {u" b": b64encode("0").decode("ascii")},
            }
        }
        self.assert_json(outputJSON)
        outputDict = json.loads(outputJSON)
        self.compare_dicts(outputDict, expectedDict)

    def test_serializer_with_tuple(self):
        value = ("test1", "test2")
        outputJSON = self.serializer.dumps(value)
        expectedDict = {" t": [{" b": b64encode("test1").decode("ascii")}, {" b": b64encode("test2").decode("ascii")}]}
        expectedJSON = self.format_json(expectedDict)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)

    def test_serializer_with_uuid(self):
        value = uuid.UUID("12345678123456781234567812345678")
        outputJSON = self.serializer.dumps(value)
        expectedDict = {" u": value.hex}
        expectedJSON = self.format_json(expectedDict)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)

    def test_serializer_with_bytes(self):
        value = b"test1"
        outputJSON = self.serializer.dumps(value)
        expectedDict = {" b": b64encode(value).decode("ascii")}
        expectedJSON = self.format_json(expectedDict)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)

    def test_serializer_with_markup(self):
        class TestMarkup:
            def __html__(self):
                return "<h1>Test</h1>"

        value = TestMarkup()
        outputJSON = self.serializer.dumps(value)
        expectedDict = {" m": text_type("<h1>Test</h1>")}
        expectedJSON = self.format_json(expectedDict)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)

    def test_serializer_with_list(self):
        value = ["test", {"key1": "value2"}]
        outputJSON = self.serializer.dumps(value)
        expectedDict = [
            {" b": b64encode("test").decode("ascii")},
            {"key1": {" b": b64encode("value2").decode("ascii")}},
        ]
        expectedJSON = self.format_json(expectedDict)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)

    def test_serializer_with_datetime(self):
        value = datetime(1990, 1, 2)
        outputJSON = self.serializer.dumps(value)
        expectedDict = {" d": http_date(value)}
        expectedJSON = self.format_json(expectedDict)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)

    def test_serializer_with_dict(self):
        value = {
            "test": {
                "foo": u"bar",
                "baz": {"foo": [9, 0, u"bar"], "bar": datetime(1990, 12, 5), "baz": {"foo": u"bar"}},
            }
        }
        outputJSON = self.serializer.dumps(value)

        expectedDict = {
            "test": {
                "foo": u"bar",
                "baz": {
                    "foo": [9, 0, u"bar"],
                    "bar": {" d": http_date(datetime(1990, 12, 5))},
                    "baz": {"foo": u"bar"},
                },
            }
        }

        self.assert_json(outputJSON)
        outputDict = json.loads(outputJSON)
        self.compare_dicts(outputDict, expectedDict)

    def test_serializer_with_str(self):
        value = "hello"
        outputJSON = self.serializer.dumps(value)
        expectedDict = {" b": b64encode(value).decode("ascii")}
        expectedJSON = self.format_json(expectedDict)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)

    def test_serializer_with_int(self):
        value = 5
        outputJSON = self.serializer.dumps(value)
        expectedValue = 5
        expectedJSON = self.format_json(expectedValue)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)

    def test_serializer_with_unicode_str(self):
        value = u"hello"
        outputJSON = self.serializer.dumps(value)
        expectedValue = u"hello"
        expectedJSON = self.format_json(expectedValue)
        self.assert_json(outputJSON)
        self.assertEqual(outputJSON, expectedJSON)
