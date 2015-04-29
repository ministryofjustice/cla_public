# -*- coding: utf-8 -*-

import urllib

from flask import current_app
from flask.ext.babel import lazy_gettext as _
import requests


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


def kwargs_to_urlparams(**kwargs):
    kwargs = dict(filter(lambda kwarg: kwarg[1], kwargs.items()))
    return urllib.urlencode(kwargs)


def laalaa_url(**kwargs):
    return '{host}/legal-advisers/?{params}'.format(
        host=current_app.config['LAALAA_API_HOST'],
        params=kwargs_to_urlparams(**kwargs))


def laalaa_search(**kwargs):
    try:
        response = requests.get(laalaa_url(**kwargs))
    except (requests.exceptions.ConnectionError,
            requests.exceptions.Timeout) as e:
        raise LaaLaaError(e)

    return response.json()


def decode_category(category):
    if category and isinstance(category, basestring):
        return PROVIDER_CATEGORIES.get(category.lower())


def decode_categories(result):
    result['categories'] = filter(None, map(
        decode_category,
        result.get('categories', [])))
    return result


def find(postcode, category=None, page=1):

    data = laalaa_search(
        postcode=postcode,
        category=category,
        page=page)

    data['results'] = map(decode_categories, data.get('results', []))

    return data
