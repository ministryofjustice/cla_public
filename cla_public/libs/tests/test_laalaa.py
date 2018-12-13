import logging
import unittest

from cla_public.app import create_app
from cla_public.libs import laalaa

logging.getLogger("MARKDOWN").setLevel(logging.WARNING)


class LaaLaaTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config/testing.py")
        self.app.config["LAALAA_API_HOST"] = "http://laalaa"
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_kwargs_to_urlparams(self):
        kwargs = {"foo": 1, "bar": 2, "quux": None}
        params = laalaa.kwargs_to_urlparams(**kwargs)
        self.assertTrue("foo=1" in params)
        self.assertTrue("bar=2" in params)
        self.assertTrue("&" in params)
        self.assertFalse("quux=None" in params)

    def test_laalaa_url(self):
        self.assertEqual("http://laalaa/legal-advisers/?foo=1", laalaa.laalaa_url(foo=1))

        self.assertEqual("http://laalaa/legal-advisers/?foo=1&bar=2", laalaa.laalaa_url(foo=1, bar=2))

    def test_decode_category(self):
        self.assertEqual("Crime", laalaa.decode_category("crm"))
        self.assertEqual("Debt", laalaa.decode_category("deb"))
        self.assertEqual(None, laalaa.decode_category("foo"))
        self.assertEqual(None, laalaa.decode_category(None))
        self.assertEqual(None, laalaa.decode_category(1))

    def test_decode_categories(self):
        result = {"categories": ["crm", "deb"]}
        laalaa.decode_categories(result)
        self.assertEqual(["Crime", "Debt"], result["categories"])

        result = {"categories": []}
        laalaa.decode_categories(result)
        self.assertEqual([], result["categories"])

        result = {}
        laalaa.decode_categories(result)
        self.assertEqual([], result["categories"])
