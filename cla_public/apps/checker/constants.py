# -*- coding: utf-8 -*-
"Categories the user needs help with"
CATEGORIES = [
    # value, label, inline help text
    (
        'aap',
        u'Actions against the police',
        u'Being treated unlawfully by authorities who detain, imprison and prosecute (for example, the police), abuse in care cases'),
    (
        'clinneg',
        u'Clinical negligence',
        u'Doctors and nurses not treating you with due care during medical treatment'),
    (
        'commcare',
        u'Community care',
        (u'You’re unhappy with the care being provided for yourself or a '
         u'relative - for example, in a care home or your own home')),
    (
        'debt',
        u'Debt',
        u'Struggling to manage or pay off debt, bankruptcy, repossession'),
    (
        'violence',
        u'Domestic violence',
        u'Abuse at home, child abuse, harassment by an ex-partner, forced marriage'),
    (
        'discrimination',
        u'Discrimination',
        (u'Being treated unfairly because of your race, sex, sexual '
         u'orientation')),
    (
        'education',
        u'Education',
        (u'Special educational needs, problems with school places, '
         u'exclusions, learning difficulties')),
    (
        'family',
        u'Family',
        u'Divorce, separation, contact with children, children being taken into care'),
    (
        'housing',
        u'Housing',
        u'Eviction, homelessness, losing your home, rent arrears'),
    (
        'immigration',
        u'Immigration and asylum',
        u'Applying for asylum or permission to stay in the UK, including for victims of human trafficking'),
    (
        'mentalhealth',
        u'Mental health',
        u'Help with mental health and mental capacity legal issues'),
    (
        'pi',
        u'Personal injury',
        u'An accident that was not your fault'),
    (
        'publiclaw',
        u'Public law',
        u'Taking legal action against a public body, like your local council'),
    (
        'benefits',
        u'Welfare benefits appeals',
        u'Appealing a decision about your benefits')
]

"Outcomes of the checker"
RESULT_OPTIONS = [
    ('eligible', u'Eligible'),
    ('ineligible', u'Ineligible'),
    ('face-to-face', u'Face-to-face'),
    ('confirmation', u'Confirmation'),
]

"Benefits"
BENEFITS_CHOICES = [
    ('income-support', u'Income Support'),
    ('jobseekers-allowance', u'Income-based Jobseeker’s Allowance'),
    ('guarantee-credit', u'Guarantee Credit'),
    ('universal-credit', u'Universal Credit'),
    ('employment-support', u'Income-related Employment and Support Allowance'),
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
    'aap'
)

YES = '1'
NO = '0'

ORGANISATION_CATEGORY_MAPPING = {
    'Abuse at home': 'Family',
    'Public law': 'Public',
    'Actions against the police': 'Action against police',
    'Welfare benefits appeals': 'Welfare benefits'
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
