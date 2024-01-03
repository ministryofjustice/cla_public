import logging
import os
import sys
import datetime

from flask import Blueprint, url_for, current_app
from flask.ext.markdown import Markdown
import jinja2

log = logging.getLogger(__name__)


def change_jinja_templates(app):
    # Change the template loader so it will seek out the MOJ Jinja
    # base templates.
    moj_loader = jinja2.ChoiceLoader([app.jinja_loader, jinja2.PackageLoader("moj_template", "templates")])

    app.jinja_env.add_extension("jinja2.ext.do")
    app.jinja_env.add_extension("jinja2.ext.i18n")

    Markdown(app, extensions=["fenced_code"])

    app.jinja_loader = moj_loader

    # we need to load a special method called "static" to mimic
    # Django; ideally we would not rely on Django-isms but the MOJ
    # template assumes you're using jinja with Django.
    import moj_template

    root_template_dir = moj_template.__path__[0]
    static_dir = os.path.join(root_template_dir, "static")
    template_dir = os.path.join(root_template_dir, "templates", "moj_template")

    moj_template_blueprint = Blueprint(
        "moj_template",
        "moj_template",
        static_folder=static_dir,
        static_url_path="/static",
        template_folder=template_dir,
    )
    app.register_blueprint(moj_template_blueprint)

    @app.context_processor
    def utility_processor():
        def static(filename):
            return url_for("moj_template.static", filename=filename)

        return {"static": static}

    # Expose user variables
    @app.context_processor
    def moj_variables():
        try:
            return app.config["APP_SETTINGS"]
        except KeyError:
            log.critical("Cannot find APP_SETTINGS group in the configuration file.")
            sys.exit(1)

    @app.context_processor
    def emergency_message_settings():
        return {
            "emergency_message_on": current_app.config["EMERGENCY_MESSAGE_ON"],
            "emergency_message_title": current_app.config["EMERGENCY_MESSAGE_TITLE"],
            "emergency_message_text": current_app.config["EMERGENCY_MESSAGE_TEXT"],
        }

    # get today's date
    @app.context_processor
    def covid_availability_times():
        show_covid_availability_times = datetime.date(year=2020, month=9, day=30) > datetime.date.today()
        return {"show_covid_availability_times": show_covid_availability_times}

    return app
