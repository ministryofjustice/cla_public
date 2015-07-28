# -*- coding: utf-8 -*-
"Base app views"

import logging
import datetime
import re
from urlparse import urlparse, urljoin

from flask import abort, current_app, jsonify, redirect, render_template, \
    session, url_for, request, views
from flask.ext.babel import lazy_gettext as _

from cla_public.apps.base import base
from cla_public.apps.base.forms import FeedbackForm, ReasonsForContactingForm
import cla_public.apps.base.filters
import cla_public.apps.base.extensions
from cla_public.apps.checker.api import post_reasons_for_contacting
from cla_public.libs import zendesk
from cla_public.libs.views import HasFormMixin, ValidFormOnOptions


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


@base.route('/online-safety')
def online_safety():
    return render_template('online-safety.html')


class ZendeskView(HasFormMixin, views.MethodView, ValidFormOnOptions):
    """
    Abstract view for Zendesk forms
    """
    template = None
    redirect_to = None

    def __init__(self):
        if not self.form_class or not self.template or not self.redirect_to:
            raise NotImplementedError
        super(ZendeskView, self).__init__()

    @property
    def default_form_data(self):
        return {'referrer': request.referrer or 'Unknown'}

    def get(self):
        return self.render_form()

    def post(self):
        error = None

        if self.form.validate_on_submit():
            response = zendesk.create_ticket(self.form.api_payload())

            if response.status_code < 300:
                return self.success_redirect()
            else:
                error = _('Something went wrong. Please try again.')

        return self.render_form(error)

    def render_form(self, error=None):
        return render_template(self.template, form=self.form, zd_error=error)

    def success_redirect(self):
        return redirect(url_for(self.redirect_to))


class Feedback(ZendeskView):
    """
    General feedback form
    """
    form_class = FeedbackForm
    template = 'feedback.html'
    redirect_to = '.feedback_confirmation'


base.add_url_rule(
    '/feedback',
    view_func=Feedback.as_view('feedback'),
    methods=('GET', 'POST', 'OPTIONS')
)


@base.route('/feedback/confirmation')
def feedback_confirmation():
    return render_template('feedback-confirmation.html')


class ReasonsForContacting(ZendeskView):
    """
    Interstitial form to ascertain why users are dropping out of
    the checker service

    NB: Shares code with Feedback view, but no longer in fact
        posts to Zendesk. If feedback is ever redirected to the
        database as well, move the code here up into ZendeskView
    """
    MODEL_REF_SESSION_KEY = 'reason_for_contact'
    GA_SESSION_KEY = 'reason_for_contact_ga'

    form_class = ReasonsForContactingForm
    template = 'reasons-for-contacting.html'
    redirect_to = 'contact.get_in_touch'

    def render_form(self, error=None):
        referrer = re.sub('^(.*:)//([A-Za-z0-9\-\.]+)(:[0-9]+)?/', '/', request.referrer or '')
        return render_template(self.template, form=self.form, referrer=referrer)

    def post(self):
        error = None
        if self.form.validate_on_submit():
            if len(self.form.reasons.data) == 0:
                # allows skipping form if nothing is selected
                return self.success_redirect()

            session[self.GA_SESSION_KEY] = ', '.join(self.form.reasons.data)
            response = post_reasons_for_contacting(form=self.form)
            # ignore if reasons not saved as they're not vital
            if response and 'reference' in response:
                session[self.MODEL_REF_SESSION_KEY] = response['reference']

            return self.success_redirect()

        return self.render_form(error)


base.add_url_rule(
    '/reasons-for-contacting',
    view_func=ReasonsForContacting.as_view('reasons_for_contacting'),
    methods=('GET', 'POST', 'OPTIONS')
)


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
    session.checker['started'] = datetime.datetime.now()
    if current_app.config.get('CONTACT_ONLY'):
        session.checker['contact_only'] = 'yes'
        return redirect(url_for('contact.get_in_touch'))
    return redirect(url_for('scope.diagnosis'))


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


@base.route('/call-me-back')
def redirect_to_contact():
    return redirect(url_for('contact.get_in_touch'))


@base.route('/status.json')
def smoke_tests():
    """
    Run smoke tests and return results as JSON datastructure
    """
    from cla_common.smoketest import smoketest
    from cla_public.apps.checker.tests.smoketests import SmokeTests

    return jsonify(smoketest(SmokeTests))
