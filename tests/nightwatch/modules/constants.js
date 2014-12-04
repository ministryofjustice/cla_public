'use strict';

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
  'income-support',
  'jobseekers-allowance',
  'guarantee-credit',
  'universal-credit',
  'employment-support',
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
      errorText: 'Not a valid amount'
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
  'income_contribution',
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
      label: 'Welfare benefits appeals',
      value: 'benefits'
    },
    link: {
      text: 'Advice Guide',
      href: 'http://www.adviceguide.org.uk'
    }
  }
];
