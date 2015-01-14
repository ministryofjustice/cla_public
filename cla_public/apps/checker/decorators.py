# -*- coding: utf-8 -*-
"CLA Public decorators"

import functools
from cla_common.constants import ELIGIBILITY_STATES

from flask import current_app, render_template, request, session, url_for, redirect

from cla_public.apps.checker.api import post_to_eligibility_check_api, post_to_is_eligible_api


def override_session_vars():
    """Allow overriding session variables with URL parameters.
    No point validating since it's only for dev testing
    """
    for key, val in request.args.items():
        session[key] = val


def form_view(form_class, form_template):
    """Convenience decorator for form views"""

    def view(fn):

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if current_app.config.get('DEBUG'):
                override_session_vars()

            form_session_data = session.get_form_data(
                form_class.__name__)

            form = form_class(request.form, **form_session_data)
            if form.is_submitted():

                if form.validate():
                    session.update_form_data(form)
                    post_to_eligibility_check_api(form)
                    return fn(session)

                else:
                    session.clear_form_data(form)

            return render_template(form_template, form=form)

        return wrapper

    return view


def redirect_if_ineligible():
    def view(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            is_eligible = post_to_is_eligible_api()
            if is_eligible == ELIGIBILITY_STATES.NO:
                return redirect(
                    url_for(
                        '.help_organisations',
                        category_name=session.category_slug))
            return fn(*args, **kwargs)

        return wrapper

    return view


def redirect_if_no_session():
    def view(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not session:
                return redirect('/session-expired')
            return fn(*args, **kwargs)

        return wrapper

    return view
