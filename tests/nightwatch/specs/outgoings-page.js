'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var constants = require('../modules/constants');

var OUTGOINGS_QUESTIONS = constants.OUTGOINGS_QUESTIONS;
var OUTGOINGS_QUESTION_ERRORS = {
  'rent': 'Enter 0 if you don’t pay rent',
  'maintenance': 'Enter 0 if this doesn’t apply to you',
  'childcare': 'Please provide an amount'
};

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  '@disabled': true,
  'Scope diagnosis': function(client) {
    client.scopeDiagnosis(constants.SCOPE_PATHS.debtInScope);
  },

  'Interstitial page': function(client) {
    client.interstitialPage();
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true);
  },

  'Income': function(client) {
    client
      .ensureCorrectPage('input[name="your_income-other_income-per_interval_value"]', '/income', {
        'h1': 'Your money coming in'
      })
      .setValue('input[name="your_income-maintenance-per_interval_value"]', 0)
      .setValue('input[name="your_income-pension-per_interval_value"]', 0)
      .setValue('input[name="your_income-other_income-per_interval_value"]', 0)
      .conditionalFormSubmit(true)
    ;
  },

  'Outgoings': function(client) {
    client.ensureCorrectPage('input[name="income_contribution"]', '/outgoings', {
      'h1': 'Your outgoings'
    });
  },

  'Childcare fields': function(client) {
    client
      .back()
      .waitForElementPresent('input[name="your_income-other_income-per_interval_value"]', 5000,
        '  - Back to /income'
      )
      .back()
      .waitForElementPresent('#have_partner-0', 5000,
        '  - Back to /about'
      )
      .setYesNoFields('have_children', 1)
      .setValue('input[name="num_children"]', 1)
      .conditionalFormSubmit(true)
      .clearValue('input[name="your_income-maintenance-per_interval_value"]')
      .clearValue('input[name="your_income-pension-per_interval_value"]')
      .clearValue('input[name="your_income-other_income-per_interval_value"]')
      .setValue('input[name="your_income-child_tax_credit-per_interval_value"]', 0)
      .setValue('input[name="your_income-maintenance-per_interval_value"]', 0)
      .setValue('input[name="your_income-pension-per_interval_value"]', 0)
      .setValue('input[name="your_income-other_income-per_interval_value"]', 0)
      .conditionalFormSubmit(true)
      .assert.visible('input[name="childcare-per_interval_value"]',
        '    - Has childcare input field'
      )
    ;
  },

  'Context-dependent text for partner': function(client) {
    client
      .assert.containsText('body', 'Money you pay your landlord',
        '  - Has help text for Rent'
      )
      .assert.containsText('body', 'Money you pay to an ex-partner for their living costs',
        '  - Has help text for Maintenance'
      )
      .assert.containsText('body', 'Money you pay per month towards your criminal legal aid',
        '  - Has help text for Monthly Income Contribution Order'
      )
      .assert.containsText('body', 'Money you pay for your child to be looked after while you work or study',
        '  - Has help text for Childcare'
      )
      .back()
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000,
        '  - Back to /income'
      )
      .back()
      .waitForElementPresent('#have_partner-0', 5000,
        '  - Back to /about'
      )
      .setYesNoFields('have_partner', 1)
      .pause(200)
      .setYesNoFields(['in_dispute', 'partner_is_employed', 'partner_is_self_employed'], 0)
      .conditionalFormSubmit(true)
      .fillInIncome(true, true, true)
      .assert.containsText('h1', 'You and your partner’s outgoings',
        '  - Has correct heading'
      )
      .assert.containsText('body', 'Money you and your partner pay your landlord',
        '  - Has help text for Rent'
      )
      .assert.containsText('body', 'Money you and/or your partner pay to an ex-partner for their living costs',
        '  - Has help text for Maintenance'
      )
      .assert.containsText('body', 'Money you and/or your partner pay per month towards your criminal legal aid',
        '  - Has help text for Monthly Income Contribution Order'
      )
      .assert.containsText('body', 'Money you and your partner pay for your child to be looked after while you work or study',
        '  - Has help text for Childcare'
      )
    ;
  },

  'Validation': function(client) {
    OUTGOINGS_QUESTIONS.forEach(function(item) {
      client.setValue(util.format('input[name=%s-per_interval_value]', item), '500');
      common.submitAndCheckForFieldError(client, [{
        name: item + '-per_interval_value',
        errorText: 'Please select a time period from the drop down'
      }]);
      client
        .clearValue(util.format('input[name=%s-per_interval_value]', item))
        .selectDropdown(item + '-interval_period', 'per_month')
      ;
      common.submitAndCheckForFieldError(client, [{
        name: item + '-per_interval_value',
        errorText: OUTGOINGS_QUESTION_ERRORS[item]
      }]);
    });

    common.submitAndCheckForFieldError(client, [{
      name: 'income_contribution',
      errorText: 'Enter 0 if this doesn’t apply to you'
    }]);

    OUTGOINGS_QUESTIONS.forEach(function(item) {
      client.setValue(util.format('input[name=%s-per_interval_value]', item), '500');
    });
    client
      .setValue('input[name="income_contribution"]', 0)
      .conditionalFormSubmit(true)
      .conditionalFormSubmit(true)
    ;

    client.end();
  }

};
