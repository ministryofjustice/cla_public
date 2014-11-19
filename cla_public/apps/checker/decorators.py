# -*- coding: utf-8 -*-
"CLA Public decorators"

import functools

from flask import current_app, render_template, request, session, url_for, redirect

from cla_public.apps.checker.api import post_to_eligibility_check_api, post_to_is_eligible_api
from cla_public.apps.checker.constants import ELIGIBILITY_INELIGIBLE


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

            form = form_class(request.form, session)
            if form.validate_on_submit():
                post_to_eligibility_check_api(form)
                is_eligible = post_to_is_eligible_api(form)
                if is_eligible == ELIGIBILITY_INELIGIBLE:
                    return redirect(url_for('.result', outcome='ineligible'))
                return fn(session)

            return render_template(form_template, form=form)

        return wrapper

    return view
