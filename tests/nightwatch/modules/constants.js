'use strict';

exports.SAVINGS_THRESHOLD = 8000;
exports.VALUABLES_MINIMUM = 500;

exports.CATEGORIES_OF_LAW = [
  {
    value: 'clinneg',
    name: 'Clinical negligence',
    covered: false
  },
  {
    value: 'commcare',
    name: 'Community care',
    covered: false
  },
  {
    value: 'debt',
    name: 'Debt',
    covered: true
  },
  {
    value: 'discrimination',
    name: 'Discrimination',
    covered: true
  },
  {
    value: 'education',
    name: 'Education',
    covered: true
  },
  {
    value: 'family',
    name: 'Family',
    covered: true
  },
  {
    value: 'housing',
    name: 'Housing',
    covered: true
  },
  {
    value: 'immigration',
    name: 'Immigration and asylum',
    covered: false
  },
  {
    value: 'mentalhealth',
    name: 'Mental health',
    covered: false
  },
  {
    value: 'pi',
    name: 'Personal injury',
    covered: false
  },
  {
    value: 'publiclaw',
    name: 'Public law',
    covered: false
  },
  {
    value: 'aap',
    name: 'Trouble with the police',
    covered: false
  },
  {
    value: 'violence',
    name: 'Domestic violence',
    covered: true
  },
  {
    value: 'benefits',
    name: 'Welfare benefits appeals',
    covered: true
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
      errorText: 'Valuable items must be at least £500'
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

exports.CHILD_BENEFIT_QUESTIONS = [
  'child_benefit',
  'child_tax_credit'
];

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
