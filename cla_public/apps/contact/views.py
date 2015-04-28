# -*- coding: utf-8 -*-
"Contact views"

from flask import abort, redirect, render_template, session, url_for, views, \
    current_app
from flask.ext.babel import lazy_gettext as _, gettext
from flask.ext.mail import Message

from cla_public.apps.contact import contact
from cla_public.apps.contact.forms import ContactForm
from cla_public.apps.checker.api import post_to_case_api, \
    post_to_eligibility_check_api, ApiError
from cla_public.apps.checker.constants import YES
from cla_public.apps.checker.views import UpdatesMeansTest
from cla_public.libs.views import AllowSessionOverride, SessionBackedFormView


@contact.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


def handle_confirmation_email(form):
    data = {
        'case_ref': session['case_ref'],
        'full_name': form.full_name.data,
        'email': form.email.data,
        'callback_requested': form.callback_requested.data == YES,
        'contact_number': form.callback.contact_number.data,
        'safe_to_contact': form.callback.safe_to_contact.data == YES,
        'callback_time':
            form.callback.time.data.strftime('%A, %d %B at %H:%M')
    }

    email_body = render_template(
        'emails/confirmation.txt',
        data=data
    )

    msg = Message(
        gettext(u'Your Civil Legal Advice reference number'),
        recipients=[(data['full_name'], data['email'])],
        body=email_body
    )

    current_app.mail.send(msg)


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
