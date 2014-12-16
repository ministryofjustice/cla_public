# -*- coding: utf-8 -*-
from flask.ext.babel import lazy_gettext as _


"Categories the user needs help with"
CATEGORIES = [
    # value, label, inline help text
    (
        'aap',
        _(u'Actions against the police'),
        _(u'Being treated unlawfully by authorities who detain, imprison and prosecute '
        u'(for example, the police), abuse in care cases')),
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
        _(u'Divorce, separation, contact with children, children being taken into care')),
    (
        'housing',
        _(u'Housing'),
        _(u'Eviction, homelessness, losing your rented home, rent arrears, being harassed '
        u'by a landlord or neighbour, health and safety issues with your home, anti-social '
        u'behaviour orders')),
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
        'benefits',
        _(u'Welfare benefits'),
        _(u'Appealing a decision made by the social security tribunal about your benefits '
        u'to the Upper Tribunal, Court of Appeal or Supreme Court'))
]

"Outcomes of the checker"
RESULT_OPTIONS = [
    ('eligible', u'Eligible'),
    ('face-to-face', u'Face-to-face'),
    ('confirmation', u'Confirmation'),
]

"Benefits"
BENEFITS_CHOICES = [
    ('income_support', u'Income Support'),
    ('job_seekers_allowance', u'Income-based Jobseeker’s Allowance'),
    ('pension_credit', u'Guarantee Credit'),
    ('universal_credit', u'Universal Credit'),
    ('employment_support', u'Income-related Employment and Support Allowance'),
    ('other-benefit', u'A different benefit not listed above'),
]

PASSPORTED_BENEFITS = [benefit for benefit, _ in BENEFITS_CHOICES[0:-1]]
NASS_BENEFITS = ('asylum-support',)

MONEY_INTERVALS = [
    ('', '-- Please select --'),
    ('per_week', 'per week'),
    ('per_4week', '4 weekly'),
    ('per_month', 'per month'),
    ('per_year', 'per year')
]

NON_INCOME_BENEFITS = [
    ('attendance', u'Attendance Allowance'),
    ('care-community', u'Care in the community Direct Payment'),
    ('carers', u'Carers’ Allowance'),
    ('constant-attendance', u'Constant Attendance Allowance'),
    ('ctax-benefits', u'Council Tax Benefits'),
    ('disability-living', u'Disability Living Allowance'),
    ('earnings-top-up', u'Earnings Top Up'),
    ('ex-severe-disablement', u'Exceptionally Severe Disablement Allowance'),
    ('fostering', u'Fostering Allowance'),
    ('housing', u'Housing Benefit'),
    ('indep-living', u'Independent Living Funds payment'),
    ('asylum-support', u'National Asylum Support Service benefit'),
    ('personal-indep', u'Personal Independent Payments'),
    ('severe-disablement', u'Severe Disablement Allowance'),
    ('social-fund', u'Social Fund Payments'),
    ('war-pension', u'War Pension'),
    ('widows-pension', u'Widow’s Pension lump sum payments'),
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

YES = '1'
NO = '0'

ORGANISATION_CATEGORY_MAPPING = {
    'Domestic violence': 'Family',
    'Public law': 'Public',
    'Actions against the police': 'Action against police',
}

DAY_TODAY = 'today'
DAY_TOMORROW = 'tomorrow'
DAY_SPECIFIC = 'specific_day'
DAY_CHOICES = (
    (DAY_TODAY, 'Call me today at'),
    (DAY_TOMORROW, 'Call me tomorrow at'),
    (DAY_SPECIFIC, 'Call me in the next week on')
)

CONTACT_SAFETY = (
    ('SAFE', 'Yes'),
    ('NO_MESSAGE', 'No'),
)
