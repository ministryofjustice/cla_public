import os
import unittest
from wtforms import StringField
from flask_wtf import Form
from mock import patch

from cla_public import app
from cla_public.apps.checker.fields import DescriptionRadioField
from cla_public.apps.checker.forms import AboutYouForm
from cla_public.libs.form_config_parser import ConfigFormMixin


FORMS_CONFIG = 'config/forms_config.yml'
FORMS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), FORMS_CONFIG)


class TestConfigForm(ConfigFormMixin, Form):
    text_field = StringField(u'Text Field')
    markdown_field = StringField(u'Markdown Field')


CHOICES = (
    (
        'text_field',
        u'Text Field',
        u'Text Field Description'),
    (
        'markdown_field',
        u'Markdown Field',
        u'Markdown Field Description'),
)


def get_en_locale():
    return 'en'


class TestDescriptionRadioFieldForm(ConfigFormMixin, Form):

    radio_select = DescriptionRadioField(
        u'Description Radio Field',
        choices=CHOICES,
        coerce=unicode)


class TestFormConfig(unittest.TestCase):

    def setUp(self):
        self.patcher = patch('cla_public.libs.utils.get_locale', get_en_locale)
        self.patcher.start()
        self.app = app.create_app('config/testing.py')
        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        self.patcher.stop()

    def test_field_more_info(self):
        form = TestConfigForm(config_path=FORMS_CONFIG_PATH)
        text_field = form._fields['text_field']
        self.assertEquals(
            text_field.more_info,
            '<p>Test text."\'][;df;lgds\'fl\'\'das</p>\n'
        )

        markdown_field = form._fields['markdown_field']
        self.assertEquals(
            markdown_field.more_info,
            '<h1>Heading for Debt Markdown</h1>\n\n<ul>\n<li>List'
            ' One</li>\n<li>Lisr Two</li>\n</ul>\n\n<p>Standard text</p>\n'
        )

    def test_description_field_more_info(self):
        form = TestDescriptionRadioFieldForm(config_path=FORMS_CONFIG_PATH)
        radio_select = form._fields['radio_select']
        for option in radio_select:
            self.assertTrue(bool(option.more_info))
            if option.field_name == 'text_field':
                self.assertEquals(
                    option.more_info,
                    '<p>Test text."\'][;df;lgds\'fl\'\'das</p>\n'
                )
            elif option.field_name == 'markdown_field':
                self.assertEquals(
                    option.more_info,
                    '<h1>Heading for Debt Markdown</h1>\n\n<ul>\n<li>List'
                    ' One</li>\n<li>Lisr Two</li>\n</ul>\n\n<p>Standard text</p>\n'
                )
