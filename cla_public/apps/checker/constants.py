# coding: utf-8
from flask.ext.babel import lazy_gettext as _
from extended_choices import Choices

# Categories the user needs help with
CATEGORIES = [
    # value, label, inline help text
    (
        "clinneg",
        _(u"Clinical negligence"),
        _(u"Doctors and nurses not treating you with due care during medical treatment"),
    ),
    (
        "commcare",
        _(u"Community care"),
        _(
            u"You’re unhappy with the care being provided for yourself or a relative due "
            u"to age, disability or special educational needs - for example, in a care "
            u"home or your own home"
        ),
    ),
    ("debt", _(u"Debt"), _(u"Bankruptcy, repossession, mortgage debt that is putting your home at risk")),
    ("violence", _(u"Domestic abuse"), _(u"Abuse at home, child abuse, harassment by an ex-partner, forced marriage")),
    (
        "discrimination",
        _(u"Discrimination"),
        _(u"Being treated unfairly because of your race, sex, sexual orientation"),
    ),
    (
        "education",
        _(u"Education"),
        _(u"Special educational needs, problems with school places, exclusions, learning difficulties"),
    ),
    ("employment", _(u"Employment"), _(u"Being treated unfairly at work, unfair dismissal, employment tribunals")),
    (
        "family",
        _(u"Family"),
        _(u"Divorce, separation, arrangements for your children, children being taken into care"),
    ),
    (
        "housing",
        _(u"Housing"),
        _(
            u"Eviction, homelessness, losing your rented home, rent arrears, harassment "
            u"by a landlord or neighbour, health and safety issues with your home"
        ),
    ),
    (
        "immigration",
        _(u"Immigration and asylum"),
        _(u"Applying for asylum or permission to stay in the UK, including for victims of human trafficking"),
    ),
    ("mentalhealth", _(u"Mental health"), _(u"Help with mental health and mental capacity legal issues")),
    ("pi", _(u"Personal injury"), _(u"An accident that was not your fault")),
    ("publiclaw", _(u"Public law"), _(u"Taking legal action against a public body, like your local council")),
    (
        "aap",
        _(u"Trouble with the police"),
        _(
            u"Being treated unlawfully by authorities who detain, imprison and prosecute "
            u"(for example, the police), abuse in care cases"
        ),
    ),
    (
        "benefits",
        _(u"Welfare benefits"),
        _(
            u"Appealing a decision made by the social security tribunal about your benefits "
            u"to the Upper Tribunal, Court of Appeal or Supreme Court"
        ),
    ),
    ("other", _(u"Any other problem"), ""),
    ("traffickingandslavery", _(u"Modern slavery"), ""),
]

# Mapping LAALAA category codes to CLA category codes
LAALAA_PROVIDER_CATEGORIES_MAP = {
    "aap": ["aap"],
    "clinneg": ["med"],
    "commcare": ["com"],
    "debt": ["deb"],
    "discrimination": ["disc"],
    "education": ["edu"],
    "family": ["mat", "fmed"],
    "housing": ["hou"],
    "immigration": ["immas"],
    "mentalhealth": ["mhe"],
    "publiclaw": ["pub"],
    "benefits": ["wb"],
    "other": ["other"],
}
"""
Add pseudo traffickingandslavery category code to map to the 'mosl' LAALAA category.
Human trafficking and modern slavery are both lumped into modern slavery.
traffickingandslavery is defined in cla_public.apps.scope.views.ScopeDiagnosis.get_category_for_larp
"""
LAALAA_PROVIDER_CATEGORIES_MAP.update({"traffickingandslavery": ["mosl"]})

# Categories that will result in the Face-to-Face route
F2F_CATEGORIES = (
    "clinneg",
    "commcare",
    "immigration",
    "mentalhealth",
    "pi",
    "publiclaw",
    "aap",
    "employment",
    "other",
)

# Outcomes of the checker
RESULT_OPTIONS = [
    ("eligible", _(u"Eligible")),
    ("face-to-face", _(u"Face-to-face")),
    ("confirmation", _(u"Confirmation")),
]

# Benefits
BENEFITS_CHOICES = [
    ("child_benefit", _(u"Child Benefit")),
    ("pension_credit", _(u"Guarantee Credit")),
    ("income_support", _(u"Income Support")),
    ("job_seekers_allowance", _(u"Income-based Jobseeker’s Allowance")),
    ("employment_support", _(u"Income-related Employment and Support Allowance")),
    ("universal_credit", _(u"Universal Credit")),
    ("other-benefit", _(u"Any other benefits")),
]

PASSPORTED_BENEFITS = [
    benefit for benefit, label in BENEFITS_CHOICES if benefit not in ["child_benefit", "other-benefit"]
]
NASS_BENEFITS = ("asylum-support",)

MONEY_INTERVALS = [
    ("", _("-- Please select --")),
    ("per_week", _("per week")),
    ("per_4week", _("4 weekly")),
    ("per_month", _("per month")),
    ("per_year", _("per year")),
]

NON_INCOME_BENEFITS = [
    ("armed-forces-independance", _(u"Armed Forces Independence payment")),
    ("attendance", _(u"Attendance Allowance")),
    ("back-to-work-bonus", _(u"Back to Work Bonus")),
    ("care-community", _(u"Care in the community Direct Payment")),
    ("carers", _(u"Carers’ Allowance")),
    ("constant-attendance", _(u"Constant Attendance Allowance")),
    ("ctax-benefits", _(u"Council Tax Benefits")),
    ("disability-living", _(u"Disability Living Allowance")),
    ("ex-severe-disablement", _(u"Exceptionally Severe Disablement Allowance")),
    ("fostering", _(u"Fostering Allowance")),
    ("housing", _(u"Housing Benefit")),
    ("indep-living", _(u"Independent Living Funds payment")),
    ("personal-indep", _(u"Personal Independence Payments")),
    ("severe-disablement", _(u"Severe Disablement Allowance")),
    ("social-fund", _(u"Social Fund Payments")),
    ("special-ed-needs", _(u"Special Education Needs (SEN) direct payment")),
    ("war-pension", _(u"War Pension")),
]

# Dont go to callback page for these cats
NO_CALLBACK_CATEGORIES = ("benefits",)

YES = "1"
NO = "0"

CATEGORY_ID_MAPPING = {"violence": "family"}

ORGANISATION_CATEGORY_MAPPING = {
    "Domestic abuse": "Family",
    "Public law": "Public",
    "Trouble with the police": "Action against police",
}

SAFE_TO_CONTACT = "SAFE"

CONTACT_PREFERENCE = Choices(
    ("CALL", "call", _(u"I’ll call CLA")),
    ("CALLBACK", "callback", _(u"Call me back")),
    ("THIRDPARTY", "thirdparty", _(u"Call someone else instead of me")),
)

LEGAL_ADVISER_SEARCH_PREFERENCE = (("location", _(u"Location")), ("organisation", _(u"Organisation")))

END_SERVICE_FLASH_MESSAGE = _(
    u"The information you have entered has not been stored on your "
    u"computer or mobile device, but your browsing history will record "
    u"that you have visited this service. If you are at risk of harm, you "
    u"should delete your browser history."
)
