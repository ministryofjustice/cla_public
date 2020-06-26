from flask import current_app, url_for

from cla_public.apps.base import base


@base.app_template_global()
def asset(filename, min_ext="min"):
    if not current_app.config["DEBUG"]:
        amended = filename.split(".")
        amended.insert(-1, min_ext)
        filename = ".".join(amended)

    return url_for("static", filename=filename)


@base.app_template_global()
def is_quick_exit_enabled(session):
    if "diagnosis_previous_choices" in session.checker:
        quick_exit_categories = ["n43n3", "n18", "n19", "n88", "n86", "n97", "n149", "n62"]
        for category in quick_exit_categories:
            if category in session.checker["diagnosis_previous_choices"]:
                return True
    return False
