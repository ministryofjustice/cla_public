# -*- coding: utf-8 -*-
"Base app views"

import logging
import datetime
from urlparse import urlparse, urljoin

from flask import abort, current_app, jsonify, redirect, render_template, \
    session, url_for, request
from flask.ext.babel import lazy_gettext as _, gettext

from cla_public.apps.base import base
from cla_public.apps.base.forms import FeedbackForm
import cla_public.apps.base.filters
import cla_public.apps.base.extensions
from cla_public.libs import zendesk


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
    error = None

    if form.validate_on_submit():
        response = zendesk.create_ticket(form.api_payload())

        if response.status_code < 300:
            return redirect(url_for('.feedback_confirmation'))
        else:
            error = _('Something went wrong. Please try again.')

    return render_template('feedback.html', form=form, zd_error=error)


@base.route('/feedback/confirmation')
def feedback_confirmation():
    return render_template('feedback-confirmation.html')


@base.route('/session')
def show_session():
    if current_app.debug:
        return jsonify(session)
    abort(404)


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


@base.route('/start')
def get_started():
    """
    Redirect to checker unless currently disabled
    """
    session.clear()
    session['started'] = datetime.datetime.now()
    if current_app.config.get('CALLMEBACK_ONLY'):
        session['callmeback_only'] = 'yes'
        return redirect(url_for('callmeback.request_callback'))
    return redirect(url_for('checker.wizard', step='problem'))


def is_safe_url(url):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, url))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def next_url():
    for url in request.values.get('next'), request.referrer:
        if url and is_safe_url(url):
            return url
    return url_for('.index')


@base.route('/locale/<locale>')
def set_locale(locale):
    """
    Set locale cookie
    """
    if locale[:2] not in [l for l, d in current_app.config['LANGUAGES']]:
        abort(404)
    response = redirect(next_url())
    expires = datetime.datetime.now() + datetime.timedelta(days=30)
    response.set_cookie('locale', locale, expires=expires)
    return response
