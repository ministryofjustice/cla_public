# -*- coding: utf-8 -*-
"CLA Public decorators"

import functools

from flask import render_template, session


def form_view(form_class, form_template):
    "Convenience decorator for form views"

    def view(fn):

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            form = form_class()
            if form.validate_on_submit():
                return fn(session)
            return render_template(form_template, form=form, user=session)

        return wrapper

    return view
