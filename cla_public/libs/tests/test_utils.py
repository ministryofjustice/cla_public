import datetime
import unittest

from cla_public.libs.utils import category_id_to_name
from cla_public.libs.call_centre_availability import (
    format_time_welsh_suffix,
    suffix_day_welsh,
    format_time_option,
    format_date_option,
)


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

    def test_welsh_ordinal(self):
        ordinals = {
            "1": "af",
            "2": "il",
            "3": "ydd",
            "4": "ydd",
            "5": "ed",
            "6": "ed",
            "7": "fed",
            "8": "fed",
            "9": "fed",
            "10": "fed",
            "11": "eg",
            "12": "fed",
            "13": "eg",
            "14": "eg",
            "15": "fed",
            "16": "eg",
            "17": "eg",
            "18": "fed",
            "19": "eg",
            "20": "fed",
        }
        for day, suffix in ordinals.iteritems():
            self.assertEqual(suffix, suffix_day_welsh(day))

        for day in range(21, 32):
            self.assertEqual(suffix_day_welsh(day), "ain")


class TestFormatTime(unittest.TestCase):
    def test_format_time_9am(self):
        date = datetime.date(2024, 1, 1)
        time = datetime.datetime.combine(date, datetime.time(9, 0))
        result = format_time_option(start_time=time)
        assert result[1] == "9am to 9.30am", result

    def test_format_time_9_30am(self):
        date = datetime.date(2024, 1, 1)
        time = datetime.datetime.combine(date, datetime.time(9, 30))
        result = format_time_option(start_time=time)
        assert result[1] == "9.30am to 10am", result

    def test_format_time_midnight(self):
        date = datetime.date(2024, 1, 1)
        time = datetime.datetime.combine(date, datetime.time(0, 0))
        result = format_time_option(start_time=time)
        assert result[1] == "12am to 12.30am", result

    def test_format_time_across_days(self):
        date = datetime.date(2024, 1, 1)
        time = datetime.datetime.combine(date, datetime.time(23, 45))
        result = format_time_option(start_time=time)
        assert result[1] == "11.45pm to 12.15am", result

    def test_format_time_across_years(self):
        date = datetime.date(2023, 12, 31)
        time = datetime.datetime.combine(date, datetime.time(23, 45))
        result = format_time_option(start_time=time)
        assert result[1] == "11.45pm to 12.15am", result


class TestFormatDate(unittest.TestCase):
    def test_format_time_9am(self):
        time = datetime.time(0, 0)
        dt = datetime.datetime.combine(datetime.date(2023, 12, 31), time)
        result = format_date_option(dt)
        assert result[1] == "Sun 31 Dec", result

    def test_format_time_9_30am(self):
        time = datetime.time(0, 0)
        dt = datetime.datetime.combine(datetime.date(2024, 1, 1), time)
        result = format_date_option(dt)
        assert result[1] == "Mon 1 Jan", result

    def test_format_time_midnight(self):
        time = datetime.time(0, 0)
        dt = datetime.datetime.combine(datetime.date(2024, 2, 29), time)
        result = format_date_option(dt)
        assert result[1] == "Thurs 29 Feb", result
