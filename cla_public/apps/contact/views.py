# -*- coding: utf-8 -*-
"Contact views"

from flask import abort, redirect, render_template, session, url_for, views, \
    current_app, flash
from flask.ext.babel import lazy_gettext as _, gettext

from cla_public.apps.contact import contact
from cla_public.apps.contact.forms import ContactForm
from cla_public.apps.checker.api import post_to_case_api, \
    post_to_eligibility_check_api, ApiError
from cla_public.apps.checker.views import UpdatesMeansTest
from cla_public.libs.views import AllowSessionOverride, SessionBackedFormView
from cla_public.apps.base.constants import END_SERVICE_FLASH_MESSAGE


@contact.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


class Contact(AllowSessionOverride, UpdatesMeansTest, SessionBackedFormView):
    form_class = ContactForm
    template = 'contact.html'

    def on_valid_submit(self):

        if self.form.extra_notes.data:
            session.checker.add_note(u'User problem', self.form.extra_notes.data)
        try:
            post_to_eligibility_check_api(session.checker.notes_object())
            post_to_case_api(self.form)
        except ApiError:
            self.form.errors['timeout'] = _(
                u'There was an error submitting your data. '
                u'Please check and try again.')
            return self.get()
        else:
            flash(END_SERVICE_FLASH_MESSAGE)

            return redirect(url_for('.confirmation'))

    def dispatch_request(self, *args, **kwargs):
        if not session:
            session.checker['force_session'] = True
        return super(Contact, self).dispatch_request(*args, **kwargs)


contact.add_url_rule(
    '/contact',
    view_func=Contact.as_view('get_in_touch'))


class ContactConfirmation(views.MethodView):

    def get(self):
        session.clear_and_store_ref()
        if not session.get('stored', {}).get('case_ref'):
            abort(404)
        return render_template('checker/result/confirmation.html')


contact.add_url_rule(
    '/result/confirmation',
    view_func=ContactConfirmation.as_view('confirmation'))
