# -*- coding: utf-8 -*-
"Contact constants"

from flask.ext.babel import lazy_gettext as _


DAY_TODAY = 'today'
DAY_SPECIFIC = 'specific_day'
DAY_CHOICES = (
    (DAY_TODAY, _('Call me today at')),
    (DAY_SPECIFIC, _('Call me in the next week on'))
)

# TODO: GET this from cla_common
THIRD_PARTY_RELATIONSHIPS = (
    ('', _(u'--- Please select ---')),
    ('PARENT_GUARDIAN', _(u'Parent or guardian')),
    ('FAMILY_FRIEND', _(u'Family member or friend')),
    ('PROFESSIONAL', _(u'Professional')),
    ('LEGAL_ADVISOR', _(u'Legal adviser')),
    ('OTHER', _(u'Other')),
)
