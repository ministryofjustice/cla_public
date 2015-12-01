'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var constants = require('../modules/constants');

var income_page_sentinel = '[name="your_income-other_income-per_interval_value"]';

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis(constants.SCOPE_PATHS.debtInScope);
  },

  'Interstitial page': function(client) {
    client.interstitialPage();
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true, {
      'on_benefits': 1
    });
  },

  'Child benefits and tax credits fields absent': function(client) {
    client
      // benefits page
      .waitForElementPresent('#benefits-0', 5000,
        '  - Page is ready'
      )
      .assert.elementNotPresent('input[name="benefits"][value="child_benefit"]',
        '  - Child benefits should not be an option')
      .selectBenefit('other-benefit', true)

      // additional benefits page
      .waitForElementVisible('#other_benefits-0', 5000,
        '  - Other Benefits page is ready'
      )
      .setYesNoFields('other_benefits', 0)
      .conditionalFormSubmit(true)
      // income page
      .assert.elementNotPresent('input[name="your_income-child_tax_credit-per_interval_value"]',
        '    - Child tax credits should not be present'
      )
    ;
  },

  'Child benefit fields': function(client) {
    client
      .back()
      // additional benefits page
      .waitForElementPresent('#benefits-0', 5000,
        '  - Other Benefits page is ready'
      )
      .back()
      // benefits page
      .waitForElementPresent('input[name="benefits"][value="pension_credit"]', 5000,
        '  - Go back to Benefits page'
      )
      .back()
      // about page
      .waitForElementPresent('#have_partner-0', 5000,
        '  - Go back to About you page'
      )
      .setYesNoFields('have_children', 1)
      .setValue('input[name="num_children"]', 1)
      // benefits page
      .conditionalFormSubmit(true)
      .selectBenefit('child_benefit', false)
      .selectBenefit('other-benefit', false)
      .waitForElementVisible('input[name="child_benefit-per_interval_value"]', 5000,
        '  - Child benefits amount should be visible')
      .setValue('[name="child_benefit-per_interval_value"]', '12')
      .selectDropdown('child_benefit-interval_period', 'per_week')
      .conditionalFormSubmit(true)
      // income page
      .waitForElementVisible('[name="your_income-child_tax_credit-per_interval_value"]', 5000,
        '    - Child tax credits should be present')
    ;
  },

  'Validation of child benefit and child tax credit fields': function(client) {
    function checkField(field, valueError) {
      client
        .setValue(util.format('input[name="%s-per_interval_value"]', field), '100')
      ;
      common.submitAndCheckForFieldError(client, [{
        name: field + '-per_interval_value',
        errorText: 'Please select a time period from the drop down'
      }]);
      client
        .clearValue(util.format('input[name="%s-per_interval_value"]', field))
        .selectDropdown(util.format('%s-interval_period', field), 'per_week')
      ;
      common.submitAndCheckForFieldError(client, [{
        name: field + '-interval_period',
        errorText: valueError
      }], 'select');
      client
        .setValue(util.format('input[name="%s-per_interval_value"]', field), '100')
      ;
    }

    client
      .startService()
      .scopeDiagnosis(constants.SCOPE_PATHS.debtInScope)
      .interstitialPage()
      .aboutSetAllToNo(false, {
        'on_benefits': 1,
        'have_dependants': 1
      })
      .setValue('input[name="num_dependants"]', 1)
      .conditionalFormSubmit(true)
      .selectBenefit('child_benefit', false);
    checkField('child_benefit', 'Please provide an amount');
    client
      .conditionalFormSubmit(true)
      .fillInIncome(undefined, undefined, false)
      .clearValue('[name="your_income-child_tax_credit-per_interval_value"]')
    ;
    checkField('your_income-child_tax_credit', 'Enter 0 if this doesn’t apply to you');
  },

  'Should also see fields if benefits=no but children=yes': function(client) {
    client
      .startService()
      .scopeDiagnosis(constants.SCOPE_PATHS.debtInScope)
      .interstitialPage()
      .aboutSetAllToNo(false, {
        'have_children': 1
      })
      .setValue('input[name="num_children"]', 1)
      .conditionalFormSubmit(true)
      .waitForElementVisible('[name="your_income-child_tax_credit-per_interval_value"]', 5000,
        '    - Child tax credits should be present')
    ;
  },

  'Should also see fields if benefits=no but dependants=yes': function(client) {
    client
      .startService()
      .scopeDiagnosis(constants.SCOPE_PATHS.debtInScope)
      .interstitialPage()
      .aboutSetAllToNo(false, {
        'have_dependants': 1
      })
      .setValue('input[name="num_dependants"]', 1)
      .conditionalFormSubmit(true)
      .waitForElementVisible('[name="your_income-child_tax_credit-per_interval_value"]', 5000,
        '    - Child tax credits should be present')
    ;
    client.end();
  }

};
