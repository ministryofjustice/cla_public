# -*- coding: utf-8 -*-
from flask.ext.babel import lazy_gettext as _, gettext

# Feedback: feel about service
FEEL_ABOUT_SERVICE_LABELS = [
    _(u'Very satisfied'),
    _(u'Satisfied'),
    _(u'Neither satisfied or dissatisfied'),
    _(u'Dissatisfied'),
    _(u'Very dissatisfied'),
]

FEEL_ABOUT_SERVICE = zip(FEEL_ABOUT_SERVICE_LABELS, FEEL_ABOUT_SERVICE_LABELS)

# Feedback: help filling in the form
HELP_FILLING_IN_FORM_LABELS = [
    _(u'No, I filled in this form myself'),
    _(u'I have difficulty using computers so someone filled in this form for me'),
    _(u'I used an accessibility tool such as a screen reader'),
    _(u'I had some other kind of help'),
]

HELP_FILLING_IN_FORM = zip(HELP_FILLING_IN_FORM_LABELS,
        HELP_FILLING_IN_FORM_LABELS)

END_SERVICE_FLASH_MESSAGE = gettext(
    u'You’ve reached the end of this service.'
    u'The information you’ve entered was automatically '
    u'deleted for your security.'
)
