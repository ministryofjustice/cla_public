import unittest

from cla_public.apps.checker.views import get_show_laalaa_link_categories


class TestInterstitial(unittest.TestCase):
    def test_should_show_laalaa_categories(self):
        self.assertEqual(
            ["debt", "discrimination", "education", "employment", "family", "housing", "violence"],
            get_show_laalaa_link_categories(),
        )
