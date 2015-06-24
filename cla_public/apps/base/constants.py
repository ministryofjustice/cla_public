# -*- coding: utf-8 -*-
from flask.ext.babel import lazy_gettext as _
from cla_common.constants import REASONS_FOR_CONTACTING

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

REASONS_FOR_CONTACTING_CHOICES = (
    # NB: these are duplicated (untranslated) in cla_common so change both when necessary!
    (REASONS_FOR_CONTACTING.CANT_ANSWER, _(u'I don’t know how to answer a question')),
    (REASONS_FOR_CONTACTING.MISSING_PAPERWORK, _(u'I don’t have the paperwork I need')),
    (REASONS_FOR_CONTACTING.PREFER_SPEAKING, _(u'I’d prefer to speak to someone')),
    (REASONS_FOR_CONTACTING.DIFFICULTY_ONLINE, _(u'I have trouble using online services')),
    (REASONS_FOR_CONTACTING.HOW_SERVICE_HELPS, _(u'I don’t understand how this service can help me')),
    (REASONS_FOR_CONTACTING.AREA_NOT_COVERED, _(u'My problem area isn’t covered')),
    (REASONS_FOR_CONTACTING.PNS, _(u'I’d prefer not to say')),
    (REASONS_FOR_CONTACTING.OTHER, _(u'Another reason')),
)
