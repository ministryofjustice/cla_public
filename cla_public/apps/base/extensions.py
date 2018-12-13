from flask import current_app, url_for

from cla_public.apps.base import base


@base.app_template_global()
def asset(filename, min_ext="min"):
    if not current_app.config["DEBUG"]:
        amended = filename.split(".")
        amended.insert(-1, min_ext)
        filename = ".".join(amended)

    return url_for("static", filename=filename)
