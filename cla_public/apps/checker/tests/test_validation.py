import os
import unittest
from mock import Mock

import flask
from werkzeug.datastructures import MultiDict
from wtforms import ValidationError, Form
from wtforms.fields.html5 import EmailField

from cla_public.apps.checker.forms import AboutYouForm
from cla_public.apps.contact.validators import EmailValidator
from cla_public.libs.utils import override_locale


def submit(**kwargs):
    return AboutYouForm(MultiDict(kwargs), csrf_enabled=False)


class TestValidation(unittest.TestCase):

    def setUp(self):
        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        config = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../../../config/forms/en/forms_config.yml'))
        app.config['FORM_CONFIG_TRANSLATIONS'] = {'en': config}
        app.babel = Mock()
        app.babel.locale_selector_func.return_value='en'
        app.extensions['babel'] = app.babel
        self.context = app.test_request_context()
        self.context.push()

    def test_too_many_kids(self):
        num = 51
        form = submit(
            have_children=True,
            num_children=num)
        form.validate()
        self.assertIn(
            u'Number must be between 1 and 50',
            form.num_children.errors,
            '{0} is not too many kids'.format(num))

    def test_email_validator(self):
        form = Form()
        field = EmailField()
        message = u'Email incorrect.'
        validator = EmailValidator(message=message)

        field.data = 'emailwithspace @example.com'
        self.assertRaises(ValidationError, validator, form, field)

        field.data = ' emailwithspace@example.com'
        self.assertRaises(ValidationError, validator, form, field)

        field.data = 'email withspace@example.com'
        self.assertRaises(ValidationError, validator, form, field)

        field.data = 'emailwithspace@ example.com'
        self.assertRaises(ValidationError, validator, form, field)

        field.data = 'emailwithspace@example.com '
        self.assertRaises(ValidationError, validator, form, field)

        field.data = 'emailwithspace@example.com'
        try:
            validator(form, field)
        except ValidationError:
            self.fail(u'%s should not raise email validation error' %
                      field.data)
