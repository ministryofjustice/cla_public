from contextlib import contextmanager
import datetime
from mock import Mock
import unittest

from wtforms.validators import ValidationError

from cla_common import call_centre_availability
from cla_public.app import create_app
from cla_public.apps.callmeback.constants import DAY_TODAY, DAY_SPECIFIC
from cla_public.apps.callmeback.fields import AvailableSlot


@contextmanager
def override_current_time(dt):
    override = lambda: dt
    original = call_centre_availability.current_datetime
    call_centre_availability.current_datetime = override
    yield
    call_centre_availability.current_datetime = original


class TestAvailability(unittest.TestCase):

    def setUp(self):
        self.app = create_app('config/testing.py')
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        self.now = datetime.datetime(2014, 11, 24, 9, 0)
        self.validator = None
        call_centre_availability.bank_holidays = lambda: \
            [datetime.datetime(2014, 12, 25, 0, 0)]

    def assertAvailable(self, time, form=None):
        form = form or Mock()
        field = Mock()
        field.data = time
        with override_current_time(self.now):
            try:
                self.validator(form, field)
            except ValidationError as e:
                self.fail('{time} was not available at {now}: {exc}'.format(
                    time=time, now=self.now, exc=e))

    def assertNotAvailable(self, time, form=None):
        form = form or Mock()
        field = Mock()
        field.data = time
        with override_current_time(self.now):
            try:
                self.validator(form, field)
            except ValidationError as e:
                pass
            else:
                self.fail('{time} was available at {now}'.format(
                    time=time, now=self.now))

    def test_available_slot_today_next_slot(self):
        self.validator = AvailableSlot(DAY_TODAY)
        self.assertAvailable(datetime.time(11, 30))

    def test_available_slot_today_before_9am(self):
        self.validator = AvailableSlot(DAY_TODAY)
        self.assertNotAvailable(datetime.time(8, 0))

    def test_available_slot_today_after_8pm(self):
        self.validator = AvailableSlot(DAY_TODAY)
        self.assertNotAvailable(datetime.time(20, 0))

    def test_available_slot_specific_day(self):
        self.validator = AvailableSlot(DAY_SPECIFIC)
        form = Mock()
        form.day.data = datetime.date(2014, 11, 25)
        self.assertAvailable(datetime.time(9, 0), form=form)

        form.day.data = datetime.date(2014, 11, 24)
        self.assertNotAvailable(datetime.time(9, 0), form=form)

        form.day.data = datetime.date(2014, 11, 30)
        self.assertNotAvailable(datetime.time(9, 0), form=form)
