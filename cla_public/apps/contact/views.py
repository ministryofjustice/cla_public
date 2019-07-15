# coding: utf-8
"Contact views"
from smtplib import SMTPAuthenticationError
from collections import Mapping

from flask import abort, redirect, render_template, session, url_for, views, current_app
from flask.ext.babel import lazy_gettext as _, gettext
from flask.ext.mail import Message

from notifications_python_client.notifications import NotificationsAPIClient

from cla_public.apps.base.views import ReasonsForContacting
from cla_public.apps.contact import contact
from cla_public.apps.contact.forms import ContactForm, ConfirmationForm
from cla_public.apps.checker.api import (
    post_to_case_api,
    post_to_eligibility_check_api,
    update_reasons_for_contacting,
    ApiError,
    AlreadySavedApiError,
    get_case_ref_from_api,
)
from cla_public.apps.checker.views import UpdatesMeansTest
from cla_public.libs.views import AllowSessionOverride, SessionBackedFormView, ValidFormOnOptions, HasFormMixin


@contact.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


def create_confirmation_email(data):
    data.update(
        {
            "case_ref": session.stored.get("case_ref"),
            "callback_requested": session.stored.get("callback_requested"),
            "contact_type": session.stored.get("contact_type"),
        }
    )

    if data.get("callback_requested"):
        data.update(
            {
                "safe_to_contact": session.stored.get("safe_to_contact"),
                "callback_time": session.stored.get("callback_time"),
            }
        )

    recipient = data["email"]

    session["confirmation_email"] = data["email"]

    return Message(
        gettext(u"Your Civil Legal Advice reference number"),
        recipients=[recipient],
        body=render_template("emails/confirmation.txt", data=data),
    )


def get_notification_client():
    return NotificationsAPIClient(current_app.config.get("GOV_NOTIFY_API_KEY"))


def send_message(message, template_id, personalisation={}):
    if not isinstance(message, Message):
        raise TypeError("message must of type Message")

    notifications_client = get_notification_client()
    personalisations = {"body": message.body, "subject": message.subject}
    personalisations.update(personalisation)
    email_address = ", ".join(message.recipients)
    return notifications_client.send_email_notification(
        email_address=email_address, template_id=template_id, personalisation=personalisations
    )


class Contact(AllowSessionOverride, UpdatesMeansTest, SessionBackedFormView):
    form_class = ContactForm
    template = "contact.html"

    def get(self, *args, **kwargs):
        if ReasonsForContacting.GA_SESSION_KEY in session:
            self.template_context = {"reasons_for_contacting": session[ReasonsForContacting.GA_SESSION_KEY]}
            del session[ReasonsForContacting.GA_SESSION_KEY]
        return super(Contact, self).get(*args, **kwargs)

    def already_saved(self):
        try:
            get_case_ref_from_api()
            session.store_checker_details()
            return redirect(url_for("contact.confirmation"))
        except ApiError:
            error_text = _(u"There was an error submitting your data. " u"Please check and try again.")

            self.form.errors["timeout"] = error_text
            return self.get()

    def add_errors(self, el, error_list):
        for error in el:
            if isinstance(error, basestring):
                error_list.append(error)
            elif isinstance(error, Mapping):
                self.add_errors(error.values(), error_list)

    def on_valid_submit(self):
        if self.form.extra_notes.data:
            session.checker.add_note(u"User problem", self.form.extra_notes.data)
        try:
            return self.post_to_api()
        except AlreadySavedApiError:
            return self.already_saved()
        except ApiError as e:
            errors = getattr(e, "errors", {})
            error_list = []
            self.add_errors(errors.values(), error_list)
            error_text = _(u"There was an error submitting your data. " u"Please check and try again.")

            if error_list:
                error_text += " - " + ", ".join(error_list)

            self.form.errors["timeout"] = error_text

            return self.get()
        except SMTPAuthenticationError:
            self.form._fields["email"].errors.append(
                _(u"There was an error submitting your email. " u"Please check and try again or try without it.")
            )
            return self.get()

    def post_to_api(self):
        if not self.form.adaptations.is_other_adaptation.data:
            self.form.adaptations.other_adaptation.data = ""
            try:
                session.checker["ContactForm"]["adaptations"]["other_adaptation"] = ""
            except KeyError:
                pass
        post_to_eligibility_check_api(session.checker.notes_object())
        post_to_case_api(self.form)
        if ReasonsForContacting.MODEL_REF_SESSION_KEY in session:
            update_reasons_for_contacting(
                session[ReasonsForContacting.MODEL_REF_SESSION_KEY], payload={"case": session.checker["case_ref"]}
            )
            del session[ReasonsForContacting.MODEL_REF_SESSION_KEY]
        session.store_checker_details()
        if self.form.email.data:
            message = create_confirmation_email(self.form.data)
            send_message(message, current_app.config["GOV_NOTIFY_TEMPLATES"]["confirmation"])
        return redirect(url_for("contact.confirmation"))

    def dispatch_request(self, *args, **kwargs):
        if not session:
            session.checker["force_session"] = True
        return super(Contact, self).dispatch_request(*args, **kwargs)


contact.add_url_rule("/contact", view_func=Contact.as_view("get_in_touch"), methods=("GET", "POST", "OPTIONS"))


class ContactConfirmation(HasFormMixin, ValidFormOnOptions, views.MethodView):

    form_class = ConfirmationForm

    def get(self):
        session.clear_checker()

        confirmation_email = session.get("confirmation_email", None)
        if confirmation_email:
            del session["confirmation_email"]
        if not session.stored.get("case_ref"):
            abort(404)
        return render_template(
            "checker/result/confirmation.html", form=self.form, confirmation_email=confirmation_email
        )

    def post(self):
        is_submitted = getattr(self.form, "is_submitted", lambda: True)
        if is_submitted() and self.form.validate():
            return self.on_valid_submit()
        return self.get()

    def on_valid_submit(self):
        if self.form.email.data and current_app.config["MAIL_SERVER"]:
            try:
                message = create_confirmation_email(self.form.data)
                send_message(message, current_app.config["GOV_NOTIFY_TEMPLATES"]["confirmation"])

            except SMTPAuthenticationError:
                self.form._fields["email"].errors.append(
                    _(u"There was an error submitting your email. " u"Please check and try again or try without it.")
                )
                return self.get()
        return redirect(url_for("contact.confirmation"))


contact.add_url_rule(
    "/result/confirmation", view_func=ContactConfirmation.as_view("confirmation"), methods=("GET", "POST", "OPTIONS")
)
