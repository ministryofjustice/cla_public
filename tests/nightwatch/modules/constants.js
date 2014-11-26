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
exports.SAVINGS_QUESTIONS = [
  {
    name: 'savings',
    errorText: 'Enter 0 if you have no savings'
  },
  {
    name: 'investments',
    errorText: 'Enter 0 if you have no investments'
  },
  {
    name: 'valuables',
    errorText: 'Not a valid amount'
  }
];
exports.EMPLOYMENT_QUESTIONS = {
  COMMON: [
    'maintenance',
    'pension',
    'other_income'
  ],
  EMPLOYED: [
    'earnings',
    'income_tax',
    'national_insurance',
    'working_tax_credit'
  ]
};
