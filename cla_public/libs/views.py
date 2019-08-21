# coding: utf-8
"Flask pluggable view mixins"

import copy
import datetime
from itertools import dropwhile, ifilter
import logging

from flask import abort, current_app, redirect, render_template, request, session, url_for, views, jsonify

log = logging.getLogger(__name__)


class EnsureSessionExists(object):
    """
    View mixin to create a session if no current one exists
    Was used on contact page which needed to be reachable directly
    from a link on the start page
    """

    def dispatch_request(self, *args, **kwargs):
        if not session or not session.is_current:
            session.clear()
            session.checker["started"] = datetime.datetime.now()
        return super(EnsureSessionExists, self).dispatch_request(*args, **kwargs)


class RequiresSession(object):
    """
    View mixin which redirects to session expired page if no session
    """

    session_expired_url = "base.session_expired"

    def dispatch_request(self, *args, **kwargs):
        if (not session or not session.is_current) and request.method.lower() != "options":
            return redirect(url_for(self.session_expired_url))
        return super(RequiresSession, self).dispatch_request(*args, **kwargs)


class HasFormMixin(object):
    form_class = None

    @property
    def form(self):
        """
        Instance of the form for this view. Prepopulated with any POST and
        session data.
        """
        if getattr(self, "_form", None) is None:
            data = {}
            if hasattr(self, "default_form_data"):
                data.update(self.default_form_data)
            data = session.checker.get(self.form_class.__name__, data)
            self._form = self.form_class(formdata=request.form, data=data)
        return self._form


class AjaxOrNormalMixin(object):
    @property
    def ajax(self):
        return request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def redirect(self, url):
        if self.ajax:
            return jsonify({"redirect": url})
        return redirect(url)

    def return_form_errors(self, *args, **kwargs):
        if self.ajax:
            return jsonify({"errors": {k: v for k, v in self.form.errors.items() if k != "csrf_token"}})
        return self.get(*args, **kwargs)


class SessionBackedFormView(AjaxOrNormalMixin, HasFormMixin, RequiresSession, views.MethodView, object):
    """
    Saves and loads form data to and from the session
    """

    template = None
    template_context = {}

    def get(self, *args, **kwargs):
        """
        Render template with form
        """
        return render_template(self.template, form=self.form, **self.template_context)

    def post(self, *args, **kwargs):
        """
        Update session with form data if valid, remove from session if not.
        """
        is_submitted = getattr(self.form, "is_submitted", lambda: True)
        if is_submitted():
            if self.form.validate():
                self.save_form_data_in_session()
                return self.on_valid_submit()
            else:
                return self.on_invalid_submit(*args, **kwargs)

        self.remove_form_data_from_session()
        return self.get(*args, **kwargs)

    def save_form_data_in_session(self):
        """
        Store the form data in the session
        """
        session.checker[self.form_class.__name__] = dict(self.form.data.items())
        session.checker[self.form_class.__name__]["is_completed"] = True

    def remove_form_data_from_session(self):
        """
        Remove the form data from the session
        """
        if self.form_class.__name__ in session.checker:
            del session.checker[self.form_class.__name__]

    def on_valid_submit(self):
        """
        Handle a valid form submission
        """
        raise NotImplementedError

    def on_invalid_submit(self, *args, **kwargs):
        self.remove_form_data_from_session()
        return self.return_form_errors(*args, **kwargs)


class AllowSessionOverride(object):
    """
    Mixin which allows overriding session vars with URL parameters
    """

    def get(self, *args, **kwargs):
        """
        Inject URL parameters into the session (if in debug mode)
        """
        if current_app.debug:
            parsed = {}
            for arg, val in request.args.items():
                form, _, field = arg.partition("_")
                parsed[form] = parsed.get(form, {})
                parsed[form].update({field: val})
            session.checker.update(parsed)

        return super(AllowSessionOverride, self).get(*args, **kwargs)


class FormWizard(SessionBackedFormView):
    """
    A sequence of forms
    """

    steps = []

    def __init__(self, name):
        super(FormWizard, self).__init__()
        self.name = name
        self._steps = {}

        def add_step(step):
            name, step = step
            step = copy.copy(step)
            step.wizard = self
            step.name = name
            self._steps[name] = step
            return step

        self.steps = map(add_step, self.steps)

    def dispatch_request(self, *args, **kwargs):
        """
        Get the form and template for the current step
        """
        step = kwargs.get("step")
        if step not in self._steps:
            abort(404)

        self.step = self._steps[step]
        self.form_class = self.step.form_class
        self.template = self.step.template
        return super(FormWizard, self).dispatch_request(*args, **kwargs)

    def get(self, *args, **kwargs):
        if hasattr(self.step, "render"):
            return self.step.render(*args, **kwargs)
        return super(FormWizard, self).get(*args, **kwargs)

    def remaining_steps(self, skip_current=False):
        """
        Get a list of the remaining steps in the wizard
        """
        if not hasattr(self, "step"):
            self.step = self.steps[0]

        def previous(step):
            return step != self.step

        def relevant(step):
            if step == self.step:
                return not skip_current
            return not self.skip(step)

        return ifilter(relevant, dropwhile(previous, self.steps))

    def next_url(self):
        """
        Get the URL for next step of the wizard
        """
        step = self.remaining_steps(skip_current=True).next()
        return self.url_for(step.name)

    def url_for(self, step_name):
        return url_for(".{0}".format(self.name), step=step_name)

    def skip(self, step):
        """
        Skip steps if certain conditions are met
        """
        return False

    def on_valid_submit(self):
        """
        Delegate handling form submission to current state
        """
        try:
            return self.step.on_valid_submit()
        except StopIteration:
            return self.complete()

    def complete(self):
        raise NotImplementedError

    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        """
        Converts the class into a view function.
        """

        def view(*args, **kwargs):
            self = view.view_class(name, *class_args, **class_kwargs)
            return self.dispatch_request(*args, **kwargs)

        if cls.decorators:
            view.__name__ = name
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        view.view_class = cls
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.methods = cls.methods
        return view


class FormWizardStep(object):
    """
    A step in a form wizard
    """

    is_completed = False

    def __init__(self, form_class, template):
        self.form_class = form_class
        self.template = template
        self.wizard = None
        self.name = None

    @property
    def form(self):
        return self.wizard.form

    def get(self, **kwargs):
        return self.wizard.get(**kwargs)

    def on_valid_submit(self):
        return self.wizard.redirect(self.wizard.next_url())
