'use strict';

exports.SAVINGS_THRESHOLD = 8000;
exports.VALUABLES_MINIMUM = 501;

exports.CATEGORIES_OF_LAW = [
  {
    value: 'clinneg',
    name: 'Clinical negligence',
    covered: false,
    headline: 'You may be able to get advice from a legal adviser'
  },
  {
    value: 'commcare',
    name: 'Community care',
    covered: false,
    headline: 'You may be able to get advice from a legal adviser'
  },
  {
    value: 'debt',
    name: 'Debt',
    covered: true,
    headline: ''
  },
  {
    value: 'discrimination',
    name: 'Discrimination',
    covered: true,
    headline: ''
  },
  {
    value: 'education',
    name: 'Education',
    covered: true,
    headline: ''
  },
  {
    value: 'family',
    name: 'Family',
    covered: true,
    headline: ''
  },
  {
    value: 'housing',
    name: 'Housing',
    covered: true,
    headline: ''
  },
  {
    value: 'immigration',
    name: 'Immigration and asylum',
    covered: false,
    headline: 'You may be able to get advice from a legal adviser',
  },
  {
    value: 'mentalhealth',
    name: 'Mental health',
    covered: false,
    headline: 'You may be able to get advice from a legal adviser',
  },
  {
    value: 'pi',
    name: 'Personal injury',
    covered: false,
    headline: 'Legal aid is not usually available for advice about personal injury',
  },
  {
    value: 'publiclaw',
    name: 'Public law',
    covered: false,
    headline: 'You may be able to get advice from a legal adviser',
  },
  {
    value: 'aap',
    name: 'Trouble with the police',
    covered: false,
    headline: 'You may be able to get advice from a legal adviser',
  },
  {
    value: 'violence',
    name: 'Domestic violence',
    covered: true,
    headline: ''
  },
  {
    value: 'benefits',
    name: 'Welfare benefits appeals',
    covered: true,
    headline: ''
  }
];

exports.ABOUT_YOU_QUESTIONS = [
  'have_partner',
  'in_dispute',
  'on_benefits',
  'have_children',
  'have_dependants',
  'have_savings',
  'have_valuables',
  'own_property',
  'is_employed',
  'is_self_employed',
  'aged_60_or_over'
];

exports.PROPERTY_QUESTIONS = [
  'properties-0-is_main_home',
  'properties-0-other_shareholders',
  'properties-0-is_rented',
  'properties-0-in_dispute'
];

exports.BENEFITS = [
  'income_support',
  'job_seekers_allowance',
  'pension_credit',
  'universal_credit',
  'employment_support',
  'other-benefit'
];

exports.SAVINGS_QUESTIONS = {
  MONEY: [
    {
      name: 'savings',
      errorText: 'Enter 0 if you have no savings'
    },
    {
      name: 'investments',
      errorText: 'Enter 0 if you have no investments'
    }
  ],
  VALUABLES: [
    {
      name: 'valuables',
      errorText: 'Enter 0 if you have no valuable items worth over £500 each'
    }
  ]
};

exports.EMPLOYMENT_QUESTIONS = {
  COMMON: [
    'maintenance',
    'pension',
    'other_income'
  ],
  EMPLOYED_MANDATORY: [
    'earnings',
    'income_tax',
    'national_insurance'
  ],
  EMPLOYED_OPTIONAL: [
    'working_tax_credit'
  ]
};

exports.OUTGOINGS_QUESTIONS = [
  'rent',
  'maintenance',
  'childcare'
];

exports.INELIGIBLE_OUTCOMES = [
  {
    category: {
      label: 'Debt',
      value: 'debt'
    },
    link: {
      text: 'Advice Guide',
      href: 'http://www.adviceguide.org.uk'
    }
  },
  {
    category: {
      label: 'Domestic violence',
      value: 'violence'
    },
    link: {
      text: 'Child Maintenance Options',
      href: 'http://www.cmoptions.org/'
    }
  },
  {
    category: {
      label: 'Discrimination',
      value: 'discrimination'
    },
    link: {
      text: 'Equality Advisory Support Service',
      href: 'http://www.equalityadvisoryservice.com/'
    }
  },
  {
    category: {
      label: 'Education',
      value: 'education'
    },
    link: {
      text: 'Independent Parental Special Education Advice (IPSEA)',
      href: 'http://www.ipsea.org.uk'
    }
  },
  {
    category: {
      label: 'Family',
      value: 'family'
    },
    link: {
      text: 'Child Maintenance Options',
      href: 'http://www.cmoptions.org/'
    }
  },
  {
    category: {
      label: 'Housing',
      value: 'housing'
    },
    link: {
      text: 'Law Centre Network',
      href: 'http://www.lawcentres.org.uk/'
    }
  },
  {
    category: {
      label: 'Welfare benefits',
      value: 'benefits'
    },
    link: {
      text: 'Advice Guide',
      href: 'http://www.adviceguide.org.uk'
    }
  }
];

exports.FORM_IDENTIFIERS = {
  'problem': 'input[name="categories"]',
  'about': 'input[name="have_partner"]',
  'benefits': 'input[name="benefits"][value="other-benefit"]',
  'additional-benefits': 'input[name="other_benefits"]',
  'property': 'input[name="properties-0-is_main_home"]',
  'savings': 'input[name="savings"]',
  'income': 'input[name="your_income-other_income-per_interval_value"]',
  'outgoings': 'input[name="income_contribution"]'
};
