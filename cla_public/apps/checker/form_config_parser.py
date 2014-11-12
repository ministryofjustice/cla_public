import os
import markdown2
import yaml


FORMS_CONFIG = 'config/forms_config.yml'
FORMS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), FORMS_CONFIG)


class FormConfigParser(object):
    """
    Converts yaml config for all forms to a form specific object

    Loads help text in to DescriptionRadioField fields
    """
    _markdown_fields = [
        'more_info'
    ]

    def __init__(self, form_name, config_path=None):
        """
        Loads form yaml file for all forms and sets the config for a specific form
        :param form_name: Class name f form
        :return: None
        """
        self.fields = {}
        self.form_config = None

        path = config_path or FORMS_CONFIG_PATH

        with open(path) as f:
            config_data = yaml.load(f.read())

        if form_name in config_data['forms']:
            self.form_config = config_data['forms'][form_name]
            # Convert markdown fields to markdown
            for field_name, field_config in self.form_config.get('fields').iteritems():
                self.fields[field_name] = self.values_to_markdown(field_config)

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

    def get_field_config(self, field_name, field=None):
        """
        Returns the config for field
        :param field_name: name of field
        :param field: passes the field to add help text for each individual radio in DescriptionRadioField fields
        :return: dict - field config for field
        """
        if field_name in self.fields:

            field_config = self.fields[field_name]

            if field and hasattr(field, 'add_more_infos'):
                # Add help text to individual radios in DescriptionRadioField fields
                more_infos = []

                field_options = field_config.get('field_options', {})
                for radio_field in field:

                    radio_field_config = field_options.get(radio_field.field_name, {})

                    more_info = radio_field_config.get('more_info', None)
                    if more_info:
                        more_infos.append(markdown2.markdown(more_info))
                    else:
                        more_infos.append(None)

                field.add_more_infos(more_infos)

            return field_config

        return {}
