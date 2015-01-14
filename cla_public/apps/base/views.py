# -*- coding: utf-8 -*-
"Base app views"

import logging
import datetime

from flask import current_app, jsonify, redirect, render_template, session, \
    url_for, request
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
    return redirect(url_for('checker.problem'))


@base.route('/toggle-welsh')
def toggle_welsh():
    """
    Toggle welsh cookie
    """
    welsh = request.cookies.get('welsh', False) == "True"
    response = redirect(url_for('.index'))
    expires = 0
    if not welsh:
        expires = datetime.datetime.now() + datetime.timedelta(days=30)
    response.set_cookie('welsh', 'True', expires=expires)
    return response
