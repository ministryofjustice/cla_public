# -*- coding: utf-8 -*-
from flask.ext.babel import lazy_gettext as _

# Feedback: feel about service
FEEL_ABOUT_SERVICE = [
    ('very_positive', _(u'Very satisfied')),
    ('positive', _(u'Satisfied')),
    ('neutral', _(u'Neither satisfied or dissatisfied')),
    ('negative', _(u'Dissatisfied')),
    ('very_negative', _(u'Very dissatisfied')),
]

# Feedback: help filling in the form
HELP_FILLING_IN_FORM = [
    ('no_help', _(u'No, I filled in this form myself')),
    ('someone_else', _(u'I have difficulty using computers so someone filled in this form for me')),
    ('accessibility_tool', _(u'I used an accessibility tool such as a screen reader')),
    ('other_help', _(u'I had some other kind of help')),
]

TIMEOUT_RETURN_ERROR = {
    'error': 'Request timeout.'
}
