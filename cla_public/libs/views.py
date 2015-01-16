# -*- coding: utf-8 -*-
"Flask pluggable view mixins"

from itertools import dropwhile, ifilter

from flask import current_app, redirect, render_template, request, session, \
    url_for, views


class SessionBackedFormView(views.MethodView, object):
    """
    Saves and loads form data to and from the session
    """

    def __init__(self, form_class=None, template=None):
        self.form_class = form_class
        self.template = template
        self._form = None
        super(SessionBackedFormView, self).__init__()

    @property
    def form(self):
        """
        Instance of the form for this view. Prepopulated with any POST and
        session data.
        """
        if self._form is None:
            self._form = self.form_class(
                request.form,
                **session.get(self.form_class.__name__, {}))
        return self._form

    def get(self, *args, **kwargs):
        """
        Render template with form
        """
        return render_template(self.template, form=self.form)

    def post(self, *args, **kwargs):
        """
        Update session with form data if valid, remove from session if not.
        """
        if self.form.validate():
            self.save_form_data_in_session()
            return self.on_valid_submit()

        self.remove_form_data_from_session()
        return self.get(*args, **kwargs)

    def save_form_data_in_session(self):
        """
        Store the form data in the session
        """
        session[self.form_class.__name__] = dict(self.form.data.items())

    def remove_form_data_from_session(self):
        """
        Remove the form data from the session
        """
        if self.form_class.__name__ in session:
            del session[self.form_class.__name__]

    def on_valid_submit(self):
        """
        Handle a valid form submission
        """
        raise NotImplementedError


class AllowSessionOverride(object):
    """
    Mixin which allows overriding session vars with URL parameters
    """

    def get(self, *args, **kwargs):
        """
        Inject URL parameters into the session (if in debug mode)
        """
        if current_app.debug:
            session.update(request.args)

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
            step.wizard = self
            step.name = name
            self._steps[name] = step
            return step

        self.steps = map(add_step, self.steps)

    def dispatch_request(self, *args, **kwargs):
        """
        Get the form and template for the current step
        """
        step = kwargs.get('step', self.steps[0].name)
        self.step = self._steps.get(step, self.steps[0])
        self.form_class = self.step.form_class
        self.template = self.step.template
        return super(FormWizard, self).dispatch_request(*args, **kwargs)

    def next_url(self):
        """
        Get the URL for next step of the wizard
        """
        previous = lambda step: step != self.step
        relevant = lambda step: step != self.step and not self.skip(step)
        step = ifilter(relevant, dropwhile(previous, self.steps)).next()

        return url_for('.{0}'.format(self.name), step=step.name)

    def skip(self, step):
        """
        Skip steps if certain conditions are met
        """
        return False

    def on_valid_submit(self):
        """
        Delegate handling form submission to current state
        """
        return self.step.on_valid_submit()

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

    def __init__(self, form_class, template):
        self.form_class = form_class
        self.template = template
        self.wizard = None
        self.name = None

    def on_valid_submit(self):
        return redirect(self.wizard.next_url())
