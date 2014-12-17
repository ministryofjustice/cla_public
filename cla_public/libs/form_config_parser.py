import os
import markdown2
import yaml

from flask import current_app, request


# mock this out for testing
def get_locale():
    return request.accept_languages.best_match(
        current_app.config.get('LANGUAGES').keys()
    ) or 'en'


class FormConfigParser(object):
    """
    Converts yaml config for all forms to a form specific object

    Loads help text in to DescriptionRadioField fields
    """
    _markdown_fields = [
        'more_info',
        'selected_notification',
    ]

    def __init__(self, form_name, config_path=None):
        """
        Loads form yaml file for all forms and sets the config for a specific form
        :param form_name: Class name f form
        :return: None
        """
        self.fields = {}
        self.form_config = None

        locale = get_locale()

        path = config_path or current_app.config['FORM_CONFIG_TRANSLATIONS'][locale]

        with open(path) as f:
            config_data = yaml.load(f.read())

        if form_name in config_data['forms']:
            self.form_config = config_data['forms'][form_name]
            # Convert markdown fields to markdown
            for field_name, field_config in self.form_config.get('fields').iteritems():
                self.fields[field_name] = self.values_to_markdown(field_config)

    def __nonzero__(self):
        return self.form_config is not None

    def values_to_markdown(self, field_config):
        """
        Converts fields in self._markdown_fields to html from markdown
        :param field_config:
        :return:
        """
        for markdown_field in self._markdown_fields:
            if markdown_field in field_config:
                field_config[markdown_field] = markdown2.markdown(field_config[markdown_field])
        return field_config

    def get(self, field_name, field=None):
        """
        Returns the config for field
        :param field_name: name of field
        :param field: passes the field to add help text for each individual radio in DescriptionRadioField fields
        :return: dict - field config for field
        """
        if field_name in self.fields:

            field_config = self.fields[field_name]

            if field and hasattr(field, 'add_options_attributes'):
                # Add help text to individual radios in DescriptionRadioField fields
                options_attributes = []

                field_options = field_config.get('field_options', {})
                for radio_field in field:
                    radio_field_config = self.values_to_markdown(field_options.get(radio_field.field_name, {}))
                    options_attributes.append(radio_field_config)

                field.add_options_attributes(options_attributes)

            return field_config

        return {}


class ConfigFormMixin(object):
    def __init__(self, *args, **kwargs):
        config_path = kwargs.pop('config_path', None)

        super(ConfigFormMixin, self).__init__(*args, **kwargs)

        config = FormConfigParser(
            self.__class__.__name__, config_path=config_path)

        if config:
            # set config attributes on the field
            for field_name, field in self._fields.iteritems():
                field.__dict__.update(config.get(field_name, field))
