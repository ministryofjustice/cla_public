# -*- coding: utf-8 -*-
"Categories the user needs help with"
CATEGORIES = [
    # value, label, inline help text
    (
        'clinneg',
        u'Clinical negligence',
        u'Doctors and nurses not treating you with due care'),
    (
        'commcare',
        u'Community care',
        (u'You’re unhappy with the care being provided for yourself or a '
         u'relative')),
    (
        'debt',
        u'Debt',
        u'Money problems, bankruptcy, repossession'),
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
        u'Divorce, separation, contact with children'),
    (
        'housing',
        u'Housing',
        u'Eviction, homelessness, losing your home, rent arrears'),
    (
        'immigration',
        u'Immigration and asylum',
        u'Applying for asylum or permission to stay in the UK'),
    (
        'mentalhealth',
        u'Mental health',
        (u'Getting someone to speak for you at a mental health tribunal or '
         u'inquest')),
    (
        'pi',
        u'Personal injury',
        u'An accident that was not your fault'),
    (
        'publiclaw',
        u'Public law',
        u'Taking legal action against a public body, like your local council'),
    (
        'aap',
        u'Trouble with the police',
        u'Being treated unfairly by the police, wrongful arrest'),
    (
        'violence',
        u'Violence or abuse at home',
        u'Domestic violence, child abuse, harassment by an ex-partner'),
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
    ('jobseekers-allowance', u'Income-based Jobseeker\'s Allowance'),
    ('guarantee-credit', u'Guarantee Credit'),
    ('universal-credit', u'Universal Credit'),
    ('employment-support', u'Income-related Employment and Support Allowance'),
    ('asylum-support', u'National Asylum Support Service benefit'),
    ('other-benefit', u'A different benefit not listed above'),
]

PASSPORTED_BENEFITS = [benefit for benefit, _ in BENEFITS_CHOICES[0:-1]]

MONEY_INTERVALS = [
    ('per week', 'per week'),
    ('4 weekly', '4 weekly'),
    ('per month', 'per month'),
    ('per year', 'per year')
]

NON_INCOME_BENEFITS = [
    ('attendance', 'Attendance Allowance'),
    ('care-community', 'Care in the community Direct Payment'),
    ('carers', 'Carers\' Allowance'),
    ('constant-attendance', 'Constant Attendance Allowance'),
    ('ctax-benefits', 'Council Tax Benefits'),
    ('disability-living', 'Disability Living Allowance'),
    ('earnings-top-up', 'Earnings Top Up'),
    ('ex-severe-disablement', 'Exceptionally Severe Disablement Allowance'),
    ('fostering', 'Fostering Allowance'),
    ('housing', 'Housing Benefit'),
    ('indep-living', 'Independent Living Funds payment'),
    ('personal-indep', 'Personal Independent Payments'),
    ('severe-disablement', 'Severe Disablement Allowance'),
    ('social-fund', 'Social Fund Payments'),
    ('war-pension', 'War Pension'),
    ('widows-pension', 'Widow\'s Pension lump sum payments'),
]

F2F_CATEGORIES = ('clinneg', 'commcare')

YES = '1'
NO = '0'
