# -*- coding: utf-8 -*-
"Contact constants"

from flask.ext.babel import lazy_gettext as _


DAY_TODAY = 'today'
DAY_SPECIFIC = 'specific_day'
DAY_CHOICES = (
    (DAY_TODAY, _('Call me today at')),
    (DAY_SPECIFIC, _('Call me in the next week on'))
)

THIRD_PARTY_RELATIONSHIPS = (
    ('', _(u'--- Please select ---')),
    ('parent_guardian', _(u'Parent or guardian')),
    ('family_friend', _(u'Family member or friend')),
    ('professional', _(u'Professional')),
    ('legal_adviser', _(u'Legal adviser')),
    ('other', _(u'Other')),
)
