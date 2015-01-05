# -*- coding: utf-8 -*-
"Base app views"

import json
import os
import logging
import datetime
import requests
import urllib

from flask import render_template, send_from_directory, current_app, \
    redirect, url_for, request, session, jsonify
from flask.ext.babel import lazy_gettext as _, gettext

from cla_public.apps.base import base
from cla_public.apps.base.decorators import api_proxy
from cla_public.apps.base.forms import FeedbackForm
from cla_public.apps.checker.api import get_ordered_organisations_by_category
import cla_public.apps.base.filters
import cla_public.apps.base.extensions
from cla_public.libs.zendesk import ZD


log = logging.getLogger(__name__)


@base.route('/')
def index():
    session.clear()
    return render_template('index.html')

@base.route('/cookies')
def cookies():
    return render_template('cookies.html')


@base.route('/privacy')
def privacy():
    return render_template('privacy.html')


@base.route('/feedback', methods=['GET', 'POST'])
def feedback():
    form = FeedbackForm()
    zd = ZD()
    zd_error = None

    if form.validate_on_submit():
        payload = form.api_payload()
        response = zd.post_to_zendesk(payload)
        zd_error = _('Something went wrong. Please try again.')

        if response.status_code < 300:
            return redirect(url_for('.feedback_confirmation'))

    return render_template('feedback.html', form=form, zd_error=zd_error)


@base.route('/feedback/confirmation')
def feedback_confirmation():
    return render_template('feedback-confirmation.html')


@base.route('/addressfinder/<path:path>', methods=['GET'])
@api_proxy(return_value=[], json_response=True)
def addressfinder_proxy_view(path):
    response = requests.get(
        '{host}/{path}?{params}'.format(
            host=current_app.config['ADDRESSFINDER_API_HOST'],
            path=path,
            params=urllib.urlencode(request.args)),
        headers={
            'Authorization': 'Token {token}'.format(
                token=current_app.config['ADDRESSFINDER_API_TOKEN'])
        },
        timeout=current_app.config.get('API_CLIENT_TIMEOUT', None)
    )
    return response.text

@base.route('/session-expired')
def session_expired():
    return render_template('session-expired.html')


@base.route('/session_keep_alive')
def session_keep_alive():
    if session and not session.permanent:
        session.permanent = True
    return jsonify({
        'session': 'OK'
    })


@base.route('/session_end')
def session_end():
    if session:
        if not session.permanent:
            session.permanent = True
        session.expires_override = \
            datetime.datetime.utcnow() + datetime.timedelta(seconds=20)
    return jsonify({
        'session': 'CLEAR'
    })
