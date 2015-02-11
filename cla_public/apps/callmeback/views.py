# -*- coding: utf-8 -*-
"CallMeBack views"

import logging

from flask import redirect, render_template, session, url_for, views
from flask.ext.babel import lazy_gettext as _
from cla_public.libs.utils import log_to_sentry
from slumber.exceptions import SlumberBaseException
from requests.exceptions import ConnectionError, Timeout

from cla_public.apps.callmeback import callmeback
from cla_public.apps.callmeback.forms import CallMeBackForm
from cla_public.apps.checker.api import post_to_case_api, \
    post_to_eligibility_check_api
from cla_public.apps.checker.views import UpdatesMeansTest
from cla_public.libs.views import AllowSessionOverride, SessionBackedFormView


log = logging.getLogger(__name__)


@callmeback.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


class CallMeBack(AllowSessionOverride, UpdatesMeansTest, SessionBackedFormView):
    form_class = CallMeBackForm
    template = 'call-me-back.html'

    def on_valid_submit(self):

        if self.form.extra_notes.data:
            session.add_note(
                u'User problem:\n{0}'.format(self.form.extra_notes.data))
        try:
            post_to_eligibility_check_api(session.notes_object())
            post_to_case_api(self.form)
        except (ConnectionError, Timeout, SlumberBaseException) as e:
            self.form.errors['timeout'] = _(
                u'There was an error submitting your data. '
                u'Please check and try again.')
            log_to_sentry(
                u'Slumber Exception on CallMeBack page: %s' % e)
            return self.get()
        else:
            return redirect(url_for('.confirmation'))

    def dispatch_request(self, *args, **kwargs):
        if not session:
            session['force_session'] = True
        return super(CallMeBack, self).dispatch_request(*args, **kwargs)



callmeback.add_url_rule(
    '/call-me-back',
    view_func=CallMeBack.as_view('request_callback'))


class CallMeBackConfirmation(views.MethodView, object):

    def get(self):
        # render template before clearing session, as we use it in the template
        response = render_template('result/confirmation.html')
        session.clear()
        return response


callmeback.add_url_rule(
    '/result/confirmation',
    view_func=CallMeBackConfirmation.as_view('confirmation'))
