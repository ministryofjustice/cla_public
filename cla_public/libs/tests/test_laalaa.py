import json
import logging
import unittest
from mock import patch

from cla_public.app import create_app
from cla_public.libs import laalaa
from cla_public.apps.checker.views import LaaLaaView

logging.getLogger("MARKDOWN").setLevel(logging.WARNING)


class LaaLaaTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app("config/testing.py")
        self.app.config["LAALAA_API_HOST"] = "http://laalaa"
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.laa_provider_categories_result = {
            "mat": "Family",
            "crm": "Crime",
            "deb": "Debt",
            "med": "Clinical negligence",
        }
        self.laalaa_search_result = json.loads(
            """{
            "count": 3,
            "next": "https://prod.laalaa.dsd.io/legal-advisers/?category=med&page=2&postcode=SW1A+1AA",
            "previous": null,
            "results": [
                {
                    "telephone": "0207 657 1555",
                    "location": {
                        "address": "50-52 Chancery Lane",
                        "city": "London",
                        "postcode": "WC2A 1HL",
                        "point": {
                            "type": "Point",
                            "coordinates": [
                                -0.112442,
                                51.517
                            ]
                        },
                        "type": "Office"
                    },
                    "organisation": {
                        "name": "Slater & Gordon (Uk) LLP",
                        "website": "www.rjw.co.uk"
                    },
                    "distance": 1.670832439304462,
                    "categories": [
                        "MED",
                        "MAT",
                        "CRM"
                    ]
                },
                {
                    "telephone": "0800 014 7070",
                    "location": {
                        "address": "55 Fleet Street",
                        "city": "London",
                        "postcode": "EC4Y 1JU",
                        "point": {
                            "type": "Point",
                            "coordinates": [
                                -0.108555,
                                51.514096
                            ]
                        },
                        "type": "Office"
                    },
                    "organisation": {
                        "name": "Hudgell Solicitors",
                        "website": "www.hudgellsolicitors.co.uk"
                    },
                    "distance": 1.683935777043317,
                    "categories": [
                        "AAP",
                        "MED"
                    ]
                },
                {
                    "telephone": "0207 405 2000",
                    "location": {
                        "address": "6 New Street Square",
                        "city": "London",
                        "postcode": "EC4A 3DJ",
                        "point": {
                            "type": "Point",
                            "coordinates": [
                                -0.108437,
                                51.51591
                            ]
                        },
                        "type": "Office"
                    },
                    "organisation": {
                        "name": "Blake Morgan LLP",
                        "website": "www.bllaw.co.uk"
                    },
                    "distance": 1.758514717561317,
                    "categories": [
                        "MED"
                    ]
                }
            ],
            "origin": {
                "postcode": "SW1A 1AA",
                "point": {
                    "type": "Point",
                    "coordinates": [
                        -0.141588,
                        51.501009
                    ]
                }
            }
        }"""
        )

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

    @patch("cla_public.libs.laalaa.get_categories")
    def test_decode_category(self, mock_get_categories):
        mock_get_categories.return_value = self.laa_provider_categories_result
        self.assertEqual("Crime", laalaa.decode_category("crm"))
        self.assertEqual("Debt", laalaa.decode_category("deb"))
        self.assertEqual(None, laalaa.decode_category("foo"))
        self.assertEqual(None, laalaa.decode_category(None))
        self.assertEqual(None, laalaa.decode_category(1))

    @patch("cla_public.libs.laalaa.get_categories")
    def test_decode_categories(self, mock_get_categories):
        mock_get_categories.return_value = self.laa_provider_categories_result
        result = {"categories": ["crm", "deb"]}
        laalaa.decode_categories(result)
        self.assertEqual(["Crime", "Debt"], result["categories"])

        result = {"categories": []}
        laalaa.decode_categories(result)
        self.assertEqual([], result["categories"])

        result = {}
        laalaa.decode_categories(result)
        self.assertEqual([], result["categories"])

    @patch("cla_public.libs.laalaa.laalaa_search")
    def test_count_in_results(self, mock_laalaa_search):
        mock_laalaa_search.return_value = self.laalaa_search_result
        with patch("cla_public.libs.laalaa.get_categories") as mock_get_categories:
            mock_get_categories.return_value = self.laa_provider_categories_result
            result = laalaa.find(postcode="SW1A 1AA", categories=["clinneg"])
            self.assertEquals(result["count"], 3)

    @patch("cla_public.libs.laalaa.laalaa_search")
    def test_search_with_no_category(self, mock_laalaa_search):
        mock_laalaa_search.return_value = self.laalaa_search_result
        with patch("cla_public.libs.laalaa.get_categories") as mock_get_categories:
            mock_get_categories.return_value = self.laa_provider_categories_result
            result = laalaa.find(postcode="SW1A 1AA")
            self.assertEquals(len(result["results"]), 3)

    @patch("cla_public.libs.laalaa.laalaa_search")
    def test_search_results_merged(self, mock_laalaa_search):
        mock_laalaa_search.return_value = self.laalaa_search_result
        with patch("cla_public.libs.laalaa.get_categories") as mock_get_categories:
            mock_get_categories.return_value = self.laa_provider_categories_result
            result = laalaa.find(postcode="SW1A 1AA", categories=["a", "b"])
            self.assertEquals(len(result["results"]), 6)
            self.assertEquals(result["count"], 6)

    def test_postcode_info_is_scottish(self):
        scottish_postcode_prefixes = LaaLaaView.get_scottish_postcode_prefixes()
        for scottish_postcode_prefix in scottish_postcode_prefixes:
            postcode_info = LaaLaaView.get_extra_postcode_context(scottish_postcode_prefix + "1AA")
            self.assertTrue(postcode_info["postcode_info"]["is_scottish_postcode"])

    def test_postcode_info_is_ni_postcode(self):
        postcode_info = LaaLaaView.get_extra_postcode_context("BT1AA")
        self.assertTrue(postcode_info["postcode_info"]["is_ni_postcode"])

    def test_postcode_info_is_mann_postcode(self):
        postcode_info = LaaLaaView.get_extra_postcode_context("IM1AA")
        self.assertTrue(postcode_info["postcode_info"]["is_mann_postcode"])

    def test_postcode_info_is_jersey_postcode(self):
        postcode_info = LaaLaaView.get_extra_postcode_context("JE1AA")
        self.assertTrue(postcode_info["postcode_info"]["is_jersey_postcode"])

    def test_postcode_info_is_guernsey_postcode(self):
        postcode_info = LaaLaaView.get_extra_postcode_context("GY1AA")
        self.assertTrue(postcode_info["postcode_info"]["is_guernsey_postcode"])
