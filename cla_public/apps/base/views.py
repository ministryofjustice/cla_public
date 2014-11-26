# -*- coding: utf-8 -*-
"Base app views"

import os
import logging
import datetime
import requests
import urllib

from flask import render_template, send_from_directory, current_app, \
    redirect, url_for, request, session, jsonify

from cla_public.apps.base import base
from cla_public.apps.base.forms import FeedbackForm
from cla_public.apps.checker.api import get_ordered_organisations_by_category
import cla_public.apps.base.filters


log = logging.getLogger(__name__)


@base.route('/<path:filename>')
def static(filename):
    # HACK: Switch to nginx.
    directory = os.path.join(current_app.static_folder, '../static-templates/')
    return send_from_directory(directory, filename)


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
    if form.validate_on_submit():
        return redirect(url_for('.index'))
    return render_template('feedback.html', form=form)

@base.route('/addressfinder/<path:path>', methods=['GET'])
def addressfinder_proxy_view(path):
    response = requests.get(
        '{host}/{path}?{params}'.format(
            host=current_app.config['ADDRESSFINDER_API_HOST'],
            path=path,
            params=urllib.urlencode(request.args)),
        headers={
            'Authorization': 'Token {token}'.format(
                token=current_app.config['ADDRESSFINDER_API_TOKEN'])
        }
    )
    return current_app.response_class(response.text,
        mimetype='application/json')

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
    if session and not session.permanent:
        session.permanent = True
    if session:
        session.expires_override = datetime.datetime.utcnow() \
                                   + datetime.timedelta(seconds=20)
    return jsonify({
        'session': 'CLEAR'
    })

@base.route('/500')
def internal_error():
    raise Exception('Foo')
