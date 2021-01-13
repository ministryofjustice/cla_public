import datetime
import unittest

from cla_public.libs.utils import category_id_to_name
from cla_public.libs.call_centre_availability import format_time_welsh_suffix


class UtilsTest(unittest.TestCase):
    def test_category_id_to_name(self):
        category_id = "clinneg"
        result = category_id_to_name(category_id)
        self.assertEquals(u"Clinical negligence", result)

    def test_format_time_welsh_suffix__morning(self):
        time = datetime.time(hour=0, minute=0)
        self.assertEqual("yb", format_time_welsh_suffix(time))

        time = datetime.time(hour=11, minute=59)
        self.assertEqual("yb", format_time_welsh_suffix(time))

    def test_format_time_welsh_suffix__afternoon(self):
        time = datetime.time(hour=12, minute=0)
        self.assertEqual("yp", format_time_welsh_suffix(time))

        time = datetime.time(hour=17, minute=59)
        self.assertEqual("yp", format_time_welsh_suffix(time))

    def test_format_time_welsh_suffix__evening_and_night(self):
        time = datetime.time(hour=18, minute=0)
        self.assertEqual("yh", format_time_welsh_suffix(time))

        time = datetime.time(hour=23, minute=59)
        self.assertEqual("yh", format_time_welsh_suffix(time))
