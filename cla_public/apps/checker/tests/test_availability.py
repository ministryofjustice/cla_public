from contextlib import contextmanager
import datetime
from mock import Mock
import unittest

from wtforms.validators import ValidationError

from cla_public.libs import call_centre_availability
from cla_public.apps.checker.constants import DAY_TODAY, DAY_TOMORROW, \
    DAY_SPECIFIC
from cla_public.apps.checker.validators import AvailableSlot


@contextmanager
def override_current_time(dt):
    override = lambda: dt
    original = call_centre_availability.current_datetime
    call_centre_availability.current_datetime = override
    yield
    call_centre_availability.current_datetime = original


def pretty(time):
    return '{:%a, %d %b %I:%M %p}'.format(time)


class TestAvailability(unittest.TestCase):

    def setUp(self):
        self.now = datetime.datetime(2014, 11, 24, 9, 0)
        self.validator = None
        call_centre_availability.bank_holidays = lambda: \
            [datetime.datetime(2014, 12, 25, 0, 0)]

    def assertAvailable(self, time, form=None):
        form = form or Mock()
        field = Mock()
        field.data = time
        with override_current_time(self.now):
            self.validator(form, field)

    def assertNotAvailable(self, time, form=None):
        form = form or Mock()
        field = Mock()
        field.data = time
        with override_current_time(self.now):
            with self.assertRaises(ValidationError):
                self.validator(form, field)

    def test_available_slot_today_next_slot(self):
        self.validator = AvailableSlot(DAY_TODAY)
        self.assertAvailable(datetime.time(10, 15))

    def test_available_slot_today_before_9am(self):
        self.validator = AvailableSlot(DAY_TODAY)
        self.assertNotAvailable(datetime.time(8, 0))

    def test_available_slot_today_after_8pm(self):
        self.validator = AvailableSlot(DAY_TODAY)
        self.assertNotAvailable(datetime.time(20, 0))

    def test_available_slot_tomorrow_9am(self):
        self.validator = AvailableSlot(DAY_TOMORROW)
        self.assertAvailable(datetime.time(9, 0))

    def test_available_slot_tomorrow_saturday_after_1230pm(self):
        self.now = datetime.datetime(2014, 11, 21, 9, 0)
        self.validator = AvailableSlot(DAY_TOMORROW)
        self.assertNotAvailable(datetime.time(13, 0))

    def test_available_slot_tomorrow_sunday(self):
        self.now = datetime.datetime(2014, 11, 22, 9, 0)
        self.validator = AvailableSlot(DAY_TOMORROW)
        self.assertNotAvailable(datetime.time(13, 0))

    def test_available_slot_specific_day(self):
        self.validator = AvailableSlot(DAY_SPECIFIC)
        form = Mock()
        form.day.data = datetime.date(2014, 11, 25)
        self.assertAvailable(datetime.time(9, 0), form=form)

        form.day.data = datetime.date(2014, 11, 24)
        self.assertNotAvailable(datetime.time(9, 0), form=form)

        form.day.data = datetime.date(2014, 11, 30)
        self.assertNotAvailable(datetime.time(9, 0), form=form)
