# -*- coding: utf-8 -*-
"CallMeBack views"

from flask import redirect, render_template, request, session, url_for

from cla_public.apps.callmeback import callmeback
from cla_public.apps.callmeback.forms import CallMeBackForm
from cla_public.apps.checker.api import post_to_case_api, \
    post_to_eligibility_check_api
from cla_public.apps.checker.decorators import form_view, \
    redirect_if_no_session


@callmeback.after_request
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response


@callmeback.route('/call-me-back', methods=['GET', 'POST'])
def request_callback():
    form_session_data = session.get_form_data('CallMeBackForm')
    form = CallMeBackForm(request.form, **form_session_data)
    if form.is_submitted():

        if form.validate():
            session.update_form_data(form)
            post_to_eligibility_check_api(form)

            if form.extra_notes.data:
                session.add_note(
                    u'User problem:\n{0}'.format(form.extra_notes.data))

            post_to_eligibility_check_api(session.notes_object())
            post_to_case_api(form)

            return redirect(url_for('.confirmation'))

        else:
            session.clear_form_data(form)

    return render_template('call-me-back.html', form=form)


@callmeback.route('/result/confirmation')
@redirect_if_no_session()
def confirmation():
    response = render_template('result/confirmation.html')
    session.clear()
    return response
