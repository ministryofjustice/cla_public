import os
import subprocess
import sys

VENV = os.environ.get("VIRTUAL_ENV", "")
LANGUAGES = [("en", "English"), ("cy", "Welsh")]

def add_msgctxt(**format_kwargs):
    """add msgctxt to pot file as babel doesn't seem to correctly add this for pgettext"""
    cmd = (
        'sed -i \'\' -e \'s/msgid "{context}"/msgctxt "{context}"\\\nmsgid "{message}"/\' '
        "cla_public/translations/messages.pot"
    )
    run(cmd.format(**format_kwargs))


def run(command, **kwargs):
    if "shell" not in kwargs:
        kwargs["shell"] = True

    return_code = subprocess.call(command, **kwargs)
    if return_code:
        sys.exit(return_code)

def make_messages():
    """compile po file."""
    run(
        "{venv}/bin/pybabel extract -F babel.cfg -k pgettext -k lazy_pgettext -k "
        "gettext -k lazy_gettext -k ugettext -k ungettext -k pugettext -k "
        "lazy_pugettext -o cla_public/translations/messages.pot --no-wrap"
        " .".format(venv=VENV)
    )

    for language_code, _ in LANGUAGES:
        run(
            "{venv}/bin/pybabel update -i cla_public/translations/messages.pot -d cla_public/translations"
            " -l {language_code} --no-wrap --no-fuzzy-matching".format(venv=VENV, language_code=language_code)
        )

if __name__ == "__main__":
    make_messages()
