from contextlib import contextmanager
import datetime
import logging
from mock import Mock
import unittest

from wtforms.validators import ValidationError

from cla_common import call_centre_availability
from cla_public.app import create_app
from cla_public.apps.contact.constants import DAY_TODAY, DAY_SPECIFIC
from cla_public.apps.contact.fields import AvailableSlot, DayChoiceField, \
    OPERATOR_HOURS
from cla_public.apps.contact.forms import ContactForm


logging.getLogger('MARKDOWN').setLevel(logging.WARNING)


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
        self.now = datetime.datetime(2014, 11, 24, 9, 30)
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
        self.assertNotAvailable(datetime.time(11, 0))
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

    def assertMondayMorningUnavailable(self, form):
        self.assertNotAvailable(datetime.time(9, 0), form=form)
        self.assertNotAvailable(datetime.time(9, 30), form=form)
        self.assertNotAvailable(datetime.time(10, 0), form=form)
        self.assertNotAvailable(datetime.time(10, 30), form=form)

    def test_monday_9to11_unavailable_after_eod_friday(self):
        times = {
            'after_hours_friday': datetime.datetime(2015, 2, 6, 20, 1),
            'saturday': datetime.datetime(2015, 2, 7, 9, 0),
            'sunday': datetime.datetime(2015, 2, 8, 9, 0)
        }
        monday = datetime.date(2015, 2, 9)
        for time in times.values():
            self.now = time
            self.validator = AvailableSlot(DAY_SPECIFIC)
            form = Mock()
            form.day.data = monday
            self.assertMondayMorningUnavailable(form)


class TestDayTimeChoices(unittest.TestCase):

    def test_day_time_choices(self):
        with override_current_time(datetime.datetime(2015, 2, 13, 21)):
            form = Mock()
            field = DayChoiceField()
            field = field.bind(form, 'day')
            choices = field.day_time_choices
            # half day on saturday
            self.assertEqual(7, len(choices['20150214']))
            # can't book before 11am on monday because we're after hours friday
            self.assertEqual(18, len(choices['20150216']))
            # can book any slot on tuesday
            self.assertEqual(22, len(choices['20150217']))


class TestCallbackInPastBug(unittest.TestCase):
    """
    Had 2 cases in which callbacks were requested in the past:
    EU-5247-5578 created 2015-02-11 23:03 for 2015-02-11 10:30
    YJ-4697-7619 created 2015-02-11 22:19 for 2015-02-11 11:00
    """

    def setUp(self):
        self.app = create_app('config/testing.py')
        self.app.test_request_context().push()

    def test_EU_5247_5578(self):
        with override_current_time(datetime.datetime(2015, 2, 11, 23, 3)):
            form = ContactForm()
            self.assertEqual([], form.callback.time.form.time_today.choices)

    def test_YJ_4697_7619(self):
        with override_current_time(datetime.datetime(2015, 2, 11, 22, 19)):
            form = ContactForm()
            self.assertEqual([], form.callback.time.form.time_today.choices)
