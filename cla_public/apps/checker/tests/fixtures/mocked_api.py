CATEGORY_LIST = [{
    "code": "immigration",
    "description": "",
    "name": "Immigration",
},
{
    "code": "abuse",
    "description": "",
    "name": "Domestic abuse",
},
{
    "code": "consumer",
    "description": "",
    "name": "Consumer",
},
{
    "code": "debt",
    "description": "You may be able to get legal aid if:\r\nYou owe money to someone who is threatening you with bankruptcy\r\nYou owe money to an individual or a mortgage lender which is putting your home at risk",
    "name": "Debt, money problems and bankruptcy",
}]


ELIGIBILITY_CHECK_CREATE = {
    'reference': '1234567890',
    'category': 'debt',
    'notes': 'lorem ipsum'
}

IS_ELIGIBILE_UNKNOWN = {
    'is_eligible' : 'unknown'
}

ELIGIBILITY_CHECK_UPDATE = {
    'reference': '1234567890',
    'category': 'debt',
    'notes': 'lorem ipsum'
}


ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_SAVINGS = {
    "reference": "1d37cc19063f4f069f374c4c0aad54d2",
    "category": None,
    "notes": "",
    "property_set": [
        {
            "value": 100000,
            "mortgage_left": 50000,
            "share": 100,
            "id": 76
        }
    ],
    "you": {
        "savings": {
            "bank_balance": 100,
            "investment_balance": 100,
            "asset_balance": 100,
            "credit_balance": 100,
        }
    },
    "partner": {
        "savings": {
            "bank_balance": 150,
            "investment_balance": 160,
            "asset_balance": 170,
            "credit_balance": 180,
        }
    },
    "dependants_young": 0,
    "dependants_old": 0
}


ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_INCOME = {
    "reference": "1d37cc19063f4f069f374c4c0aad54d2",
    "category": None,
    "notes": "",
    "property_set": [
        {
            "value": 100000,
            "mortgage_left": 50000,
            "share": 100,
            "id": 76
        }
    ],
    "you": {
        "income": {
            "earnings": {'interval_period': u'per_4week',
                         'per_interval_value': 22200,
                         'per_month': 22200
                        },
            "other_income": 333,
            "self_employed": False,
        }
    },
    "partner": {
        "income": {
            "earnings": {'interval_period': u'per_week',
                         'per_interval_value': 44400,
                         'per_month': 44400
                        },
            "other_income": 555,
            "self_employed": False,
        }
    },
    "dependants_young": 3,
    "dependants_old": 2
}


ELIGIBILITY_CHECK_UPDATE_FROM_YOUR_ALLOWANCES = {
    "reference": "1d37cc19063f4f069f374c4c0aad54d2",
    "category": None,
    "notes": "",
    "property_set": [],
    "you": {
        "deductions": {
            "income_tax_and_ni": 100,
            "maintenance": 100,
            "childcare": 100,
            "mortgage_or_rent": 100,
            "criminal_legalaid_contributions": 100
        }
    },
    "dependants_young": 0,
    "dependants_old": 0
}


ELIGIBILITY_CHECK_CREATE_CASE = {
    "eligibility_check": "1d37cc19063f4f069f374c4c0aad54d2",
    "personal_details": {
        "title": "mr",
        "full_name": "John Doe",
        "postcode": "SW1H 9AJ",
        "street": "102 Petty France",
        "mobile_phone": "0123456789",
        "home_phone": "9876543210"
    },
    "reference": "LA-2954-3453"
}

IS_ELIGIBLE_YES = {
    'is_eligible': 'yes'
}

IS_ELIGIBLE_NO = {
    'is_eligible': 'no'
}

IS_ELIGIBLE_UNKNOWN = {
    'is_eligible': 'unknown'
}
