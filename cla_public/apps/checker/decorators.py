# -*- coding: utf-8 -*-
"CLA Public decorators"

import functools

from flask import current_app, render_template, request, session


def form_view(form_class, form_template):
    "Convenience decorator for form views"

    def view(fn):

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):

            if current_app.config.get('DEBUG'):
                # allow overriding session variables
                # no point validating since it's only for dev testing
                for key, val in request.args.items():
                    session[key] = val

            form = form_class(request.form, session)
            if form.validate_on_submit():
                return fn(session)
            return render_template(form_template, form=form)

        return wrapper

    return view
