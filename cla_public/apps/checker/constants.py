# -*- coding: utf-8 -*-
from flask.ext.babel import lazy_gettext as _, lazy_pgettext


"Categories the user needs help with"
CATEGORIES = [
    # value, label, inline help text
    (
        'clinneg',
        _(u'Clinical negligence'),
        _(u'Doctors and nurses not treating you with due care during medical treatment')),
    (
        'commcare',
        _(u'Community care'),
        _(u'You’re unhappy with the care being provided for yourself or a relative due '
        u'to age, disability or special educational needs - for example, in a care '
        u'home or your own home')),
    (
        'debt',
        _(u'Debt'),
        _(u'Bankruptcy, repossession, mortgage debt that is putting your home at risk')),
    (
        'violence',
        _(u'Domestic violence'),
        _(u'Abuse at home, child abuse, harassment by an ex-partner, forced marriage')),
    (
        'discrimination',
        _(u'Discrimination'),
        _(u'Being treated unfairly because of your race, sex, sexual '
        u'orientation')),
    (
        'education',
        _(u'Education'),
        _(u'Special educational needs, problems with school places, '
        u'exclusions, learning difficulties')),
    (
        'employment',
        _(u'Employment'),
        _(u'Being treated unfairly at work, unfair dismissal, employment tribunals')),
    (
        'family',
        _(u'Family'),
        _(u'Divorce, separation, arrangements for your children, children being taken into care')),
    (
        'housing',
        _(u'Housing'),
        _(u'Eviction, homelessness, losing your rented home, rent arrears, harassment '
          u'by a landlord or neighbour, health and safety issues with your home')),
    (
        'immigration',
        _(u'Immigration and asylum'),
        _(u'Applying for asylum or permission to stay in the UK, including for victims of '
        u'human trafficking')),
    (
        'mentalhealth',
        _(u'Mental health'),
        _(u'Help with mental health and mental capacity legal issues')),
    (
        'pi',
        _(u'Personal injury'),
        _(u'An accident that was not your fault')),
    (
        'publiclaw',
        _(u'Public law'),
        _(u'Taking legal action against a public body, like your local council')),
    (
        'aap',
        _(u'Trouble with the police'),
        _(u'Being treated unlawfully by authorities who detain, imprison and prosecute '
          u'(for example, the police), abuse in care cases')),
    (
        'benefits',
        _(u'Welfare benefits'),
        _(u'Appealing a decision made by the social security tribunal about your benefits '
        u'to the Upper Tribunal, Court of Appeal or Supreme Court'))
]

"Outcomes of the checker"
RESULT_OPTIONS = [
    ('eligible', _(u'Eligible')),
    ('face-to-face', _(u'Face-to-face')),
    ('confirmation', _(u'Confirmation')),
]

"Benefits"
BENEFITS_CHOICES = [
    ('income_support', _(u'Income Support')),
    ('job_seekers_allowance', _(u'Income-based Jobseeker’s Allowance')),
    ('pension_credit', _(u'Guarantee Credit')),
    ('universal_credit', _(u'Universal Credit')),
    ('employment_support', _(u'Income-related Employment and Support Allowance')),
    ('other-benefit', _(u'A different benefit not listed above')),
]

PASSPORTED_BENEFITS = [benefit for benefit, label in BENEFITS_CHOICES[0:-1]]
NASS_BENEFITS = ('asylum-support',)

MONEY_INTERVALS = [
    ('', _('-- Please select --')),
    ('per_week', _('per week')),
    ('per_4week', _('4 weekly')),
    ('per_month', _('per month')),
    ('per_year', _('per year'))
]

NON_INCOME_BENEFITS = [
    ('armed-forces-independance', _(u'Armed Forces Independence payment')),
    ('attendance', _(u'Attendance Allowance')),
    ('back-to-work-bonus', _(u'Back to Work Bonus')),
    ('care-community', _(u'Care in the community Direct Payment')),
    ('carers', _(u'Carers’ Allowance')),
    ('constant-attendance', _(u'Constant Attendance Allowance')),
    ('ctax-benefits', _(u'Council Tax Benefits')),
    ('disability-living', _(u'Disability Living Allowance')),
    ('ex-severe-disablement', _(u'Exceptionally Severe Disablement Allowance')),
    ('fostering', _(u'Fostering Allowance')),
    ('housing', _(u'Housing Benefit')),
    ('indep-living', _(u'Independent Living Funds payment')),
    ('personal-indep', _(u'Personal Independent Payments')),
    ('severe-disablement', _(u'Severe Disablement Allowance')),
    ('social-fund', _(u'Social Fund Payments')),
    ('special-ed-needs', _(u'Special Education Needs (SEN) direct payment')),
    ('war-pension', _(u'War Pension')),
]

F2F_CATEGORIES = (
    'clinneg',
    'commcare',
    'immigration',
    'mentalhealth',
    'pi',
    'publiclaw',
    'aap',
    'employment',
)

"Dont go to callback page for these cats"
NO_CALLBACK_CATEGORIES = ('benefits',)

YES = '1'
NO = '0'

ORGANISATION_CATEGORY_MAPPING = {
    'Domestic violence': 'Family',
    'Public law': 'Public',
    'Trouble with the police': 'Action against police',
}

CONTACT_SAFETY = (
    ('SAFE', lazy_pgettext(context=u'It is', string=u'Yes')),
    ('NO_MESSAGE', lazy_pgettext(context=u"It isn’t", string=u'No')),
)

CONTACT_PREFERENCE = (
    (NO, _(u'I’ll call CLA')),
    (YES, _(u'Call me back')),
)

LEGAL_ADVISER_SEARCH_PREFERENCE = (
    ('location', _(u'Location')),
    ('organisation', _(u'Organisation')),
)
