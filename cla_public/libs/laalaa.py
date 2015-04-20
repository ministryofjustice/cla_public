# -*- coding: utf-8 -*-

import requests
from flask import current_app
from flask.ext.babel import lazy_gettext as _


PROVIDER_CATEGORIES = {
    'aap': _('Actions against the police'),
    'med': _('Clinical negligence'),
    'com': _('Community care'),
    'crm': _('Crime'),
    'deb': _('Debt'),
    'mat': _('Family'),
    'fmed': _('Family mediation'),
    'hou': _('Housing'),
    'immas': _('Immigration or asylum'),
    'mhe': _('Mental health'),
    'pl': _('Prison law'),
    'pub': _('Public law'),
    'wb': _('Welfare benefits')
}

class LaaLaaError(Exception):
    pass


def find(postcode, category, page=1):
    def decode_category(code):
        return PROVIDER_CATEGORIES.get(code.lower())

    try:
        response = requests.get(
            '{host}/legal-advisers/?postcode={postcode}&page={page}&category={category}&format=json'
            .format(
                host=current_app.config['LAALAA_API_HOST'],
                postcode=postcode,
                category=category,
                page=page
            )
        )
        try:
            data = response.json()

            for result in data.get('results', []):
                if result.get('categories'):
                    result['categories'] = map(decode_category, result['categories'])

            return data

        except ValueError:
            raise LaaLaaError
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout) as e:
        raise LaaLaaError(e)
