import os
import unittest
from wtforms import StringField

from cla_public import app
from cla_public.apps.checker.fields import DescriptionRadioField
from cla_public.apps.checker.forms import ConfigForm


FORMS_CONFIG = 'config/forms_config.yml'
FORMS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), FORMS_CONFIG)


class TestConfigForm(ConfigForm):
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


class TestDescriptionRadioFieldForm(ConfigForm):

    radio_select = DescriptionRadioField(
        u'Description Radio Field',
        choices=CHOICES,
        coerce=unicode)


class TestFormConfig(unittest.TestCase):

    def setUp(self):
        self.app = app.create_app('FLASK_TEST')
        self._ctx = self.app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        pass

    def test_field_help_text(self):
        form = TestConfigForm(config_path=FORMS_CONFIG_PATH)
        text_field = form._fields['text_field']
        self.assertEquals(
            text_field.help_text,
            '<p>Test text."\'][;df;lgds\'fl\'\'das</p>\n'
        )

        markdown_field = form._fields['markdown_field']
        self.assertEquals(
            markdown_field.help_text,
            '<h1>Heading for Debt Markdown</h1>\n\n<ul>\n<li>List'
            ' One</li>\n<li>Lisr Two</li>\n</ul>\n\n<p>Standard text</p>\n'
        )

    def test_description_field_help_text(self):
        form = TestDescriptionRadioFieldForm(config_path=FORMS_CONFIG_PATH)
        radio_select = form._fields['radio_select']
        for option in radio_select:
            self.assertTrue(bool(option.help_text))
            if option.field_name == 'text_field':
                self.assertEquals(
                    option.help_text,
                    '<p>Test text."\'][;df;lgds\'fl\'\'das</p>\n'
                )
            elif option.field_name == 'markdown_field':
                self.assertEquals(
                    option.help_text,
                    '<h1>Heading for Debt Markdown</h1>\n\n<ul>\n<li>List'
                    ' One</li>\n<li>Lisr Two</li>\n</ul>\n\n<p>Standard text</p>\n'
                )




