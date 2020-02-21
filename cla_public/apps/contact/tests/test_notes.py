from werkzeug.datastructures import MultiDict

from cla_public.apps.contact.forms import ContactForm
from cla_public.apps.base.tests import FlaskAppTestCase


def submit(**kwargs):
    return ContactForm(MultiDict(kwargs), csrf_enabled=False)


class NotesTest(FlaskAppTestCase):
    def validate_notes(self, notes):
        form = submit(extra_notes=notes)
        form.validate()
        return u"Your notes must be 4000 characters or less" not in form.extra_notes.errors

    def test_notes_max_length(self):
        longest_allowed = "x" * 4000
        self.assertTrue(self.validate_notes(longest_allowed))

        too_long = longest_allowed + "x"
        self.assertFalse(self.validate_notes(too_long))
