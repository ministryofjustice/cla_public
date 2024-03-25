from unittest import TestCase
from mock import patch
import datetime
from cla_public.apps.contact.api import get_valid_callback_days, get_valid_callback_timeslots_on_date


class TestGetValidCallbackDays(TestCase):
    def test_full_week(self):
        full_week_of_datetimes = [datetime.datetime(2024, 1, day, 9, 0) for day in range(1, 7)]
        with patch("cla_public.apps.contact.api.get_valid_callback_slots", return_value=full_week_of_datetimes):
            valid_days = get_valid_callback_days()
            for index, day in enumerate(valid_days):
                assert day.date() == full_week_of_datetimes[index].date()

    def test_no_valid_days_week(self):
        no_valid_slots = []
        with patch("cla_public.apps.contact.api.get_valid_callback_slots", return_value=no_valid_slots):
            valid_days = get_valid_callback_days()
        assert valid_days == []

    def test_single_day(self):
        valid_slots = [datetime.datetime(2024, 1, 1, hour, 0) for hour in range(9, 19)]
        with patch("cla_public.apps.contact.api.get_valid_callback_slots", return_value=valid_slots):
            valid_days = get_valid_callback_days()
        for index, day in enumerate(valid_days):
            assert day.date() == valid_slots[index].date()


class TestGetValidCallbackTimeslotsOnDate(TestCase):
    def test_single_day(self):
        date = datetime.date(2024, 1, 1)
        valid_slots = [datetime.datetime.combine(date, datetime.time(hour, 0)) for hour in range(9, 19)]
        with patch("cla_public.apps.contact.api.get_valid_callback_slots", return_value=valid_slots):
            slots_on_date = get_valid_callback_timeslots_on_date(date=date)
        for index, slot in enumerate(slots_on_date):
            assert slot == valid_slots[index]

    def test_multiple_days(self):
        date_1 = datetime.date(2024, 1, 1)
        date_2 = datetime.date(2024, 1, 2)
        slots_on_date_1 = [datetime.datetime.combine(date_1, datetime.time(hour, 0)) for hour in range(9, 19)]
        slots_on_date_2 = [datetime.datetime.combine(date_2, datetime.time(hour, 0)) for hour in range(9, 19)]
        with patch(
            "cla_public.apps.contact.api.get_valid_callback_slots", return_value=slots_on_date_1 + slots_on_date_2
        ):
            slots_on_date = get_valid_callback_timeslots_on_date(date=date_2)
        for slot in slots_on_date:
            assert slot in slots_on_date_2
            assert slot not in slots_on_date_1
