import functools

from flask import render_template, session

from cla_public.apps.checker.models import UserStatus


def form_view(form_class, form_template):
    "Convenience decorator for form views"

    def view(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):

            form = form_class()
            user_status = UserStatus(session.get('status', {}))
            if form.validate_on_submit():
                user_status.update(form)
                session['status'] = user_status
                return fn(user_status)
            return render_template(form_template, form=form, user=user_status)

        return wrapper

    return view
