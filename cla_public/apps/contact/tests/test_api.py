from unittest import TestCase
from mock import patch
import datetime
from cla_public.apps.contact.api import get_valid_callback_days


class TestGetValidCallbackDays(TestCase):
    def test_full_week(self):
        full_week_of_datetimes = [datetime.datetime(2024, 1, day, 9, 0) for day in range(1, 7)]
        with patch('cla_public.apps.contact.api.get_valid_callback_slots', return_value=full_week_of_datetimes):
            valid_days = get_valid_callback_days()
            for index, day in enumerate(valid_days):
                assert day.date() == full_week_of_datetimes[index].date()
        