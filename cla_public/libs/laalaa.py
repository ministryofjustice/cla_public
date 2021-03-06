# coding: utf-8
from flask import current_app
from flask.ext.babel import lazy_gettext as _
import requests
from werkzeug.urls import url_encode

from cla_common.laalaa import LaalaaProviderCategoriesApiClient, LaaLaaError


def kwargs_to_urlparams(**kwargs):
    kwargs = dict(filter(lambda kwarg: kwarg[1], kwargs.items()))
    return url_encode(kwargs)


def laalaa_url(**kwargs):
    return "{host}/legal-advisers/?{params}".format(
        host=current_app.config["LAALAA_API_HOST"], params=kwargs_to_urlparams(**kwargs)
    )


def laalaa_search(**kwargs):
    try:
        response = requests.get(laalaa_url(**kwargs))
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        raise LaaLaaError(e)


def get_categories():
    client = LaalaaProviderCategoriesApiClient.singleton(current_app.config["LAALAA_API_HOST"], category_translator=_)
    return client.get_categories()


def decode_category(category):
    if category and isinstance(category, basestring):
        categories = get_categories()
        return categories.get(category.lower())


def decode_categories(result):
    result["categories"] = filter(None, map(decode_category, result.get("categories", [])))
    return result


def find(postcode, categories=None, page=1):
    if not categories:
        categories = [None]
    merged_data = {"results": [], "count": 0}
    for category in categories:
        data = laalaa_search(postcode=postcode, category=category, page=page)
        merged_data["results"].extend(map(decode_categories, data.get("results", [])))
        merged_data["origin"] = data.get("origin")
        merged_data["count"] += data.get("count", 0)
    return merged_data
