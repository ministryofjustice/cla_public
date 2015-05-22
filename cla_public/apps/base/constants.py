# -*- coding: utf-8 -*-
from flask.ext.babel import lazy_gettext as _

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


REASONS_FOR_CONTACTING_OTHER = u'Other reason (please specify)'
REASONS_FOR_CONTACTING_NONE = u'None of the above'
REASONS_FOR_CONTACTING = [
    u'I didn’t know how to answer a question',
    u'I don’t have the necessary paperwork with me',
    u'I’d prefer to speak to someone',
    u'I have difficulty in using online services without help',
    u'I don’t understand how this service can help me',
    u'It didn’t cover or mention my problem area',
    REASONS_FOR_CONTACTING_OTHER,
    REASONS_FOR_CONTACTING_NONE,
]
# NB: keys are deliberately not localised
REASONS_FOR_CONTACTING = map(lambda reason: (reason, _(reason)), REASONS_FOR_CONTACTING)
