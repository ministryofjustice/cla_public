'use strict';

var util = require('util');
var common = require('../modules/common-functions');

var income_page_sentinel = '[name="your_income-other_income-per_interval_value"]';

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes']);
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
      .waitForElementPresent('input[name="benefits"]', 5000)
      .assert.elementNotPresent('input[name="benefits"][value="child_benefit"]',
        'Child benefits should not be an option')
      .selectBenefit('other-benefit', true)

      // additional benefits page
      .waitForElementVisible('input[name="other_benefits"]', 5000)
      .setYesNoFields('other_benefits', 0)
      .submitForm('form')

      // income page
      .waitForElementVisible('[name="your_income-other_income-per_interval_value"]', 5000)
      .assert.elementNotPresent('input[name="your_income-child_tax_credit-per_interval_value"]',
        'Child tax credits should not be present')
      .assert.elementNotPresent('input[name="your_income-child_tax_credit-interval_period"]',
        'Child tax credits should not be present');
  },

  'Child benefit fields': function(client) {
    client
      .back()
      // additional benefits page
      .waitForElementPresent('input[name="benefits"]', 5000)
      .back()
      // benefits page
      .waitForElementPresent('input[name="benefits"]', 5000)
      .back()
      // about page
      .waitForElementPresent('input[name="have_partner"]', 5000)
      .setYesNoFields('have_children', 1)
      .setValue('input[name="num_children"]', 1)
      .submitForm('form')

      // benefits page
      .waitForElementVisible('input[name="benefits"][value="child_benefit"]', 5000,
        'Child benefits should be an option')
      .selectBenefit('child_benefit', false)
      .selectBenefit('other-benefit', false)
      .waitForElementVisible('input[name="child_benefit-per_interval_value"]', 5000,
        'Child benefits amount should be visible')
      .setValue('[name="child_benefit-per_interval_value"]', '12')
      .setValue('[name="child_benefit-interval_period"]', 'per week')
      .submitForm('form')

      // income page
      .waitForElementVisible(income_page_sentinel, 5000,
        'Income page should show')
      .waitForElementVisible('[name="your_income-child_tax_credit-per_interval_value"]', 5000,
        'Child tax credits should be present')
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
        .click(util.format('select[name="%s-interval_period"] option:first-child + option', field))
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
      .scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes'])
      .interstitialPage()
      .aboutSetAllToNo(false, {
        'on_benefits': 1,
        'have_dependants': 1
      })
      .setValue('input[name="num_dependants"]', 1)
      .submitForm('form')
      .selectBenefit('child_benefit', false);
    checkField('child_benefit', 'Please provide an amount');
    client
      .submitForm('form')
      .fillInIncome(undefined, undefined, false)
      .clearValue('[name="your_income-child_tax_credit-per_interval_value"]')
      .click('select[name="your_income-child_tax_credit-interval_period"] option:first-child');
    checkField('your_income-child_tax_credit', 'Enter 0 if this doesn’t apply to you');
  },

  'Should also see fields if benefits=no but children=yes': function(client) {
    client
      .startService()
      .scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes'])
      .interstitialPage()
      .aboutSetAllToNo(false, {
        'have_children': 1
      })
      .setValue('input[name="num_children"]', 1)
      .submitForm('form')
      .waitForElementVisible(income_page_sentinel, 5000,
        'Income page should show')
      .waitForElementVisible('[name="your_income-child_tax_credit-per_interval_value"]', 5000,
        'Child tax credits should be present')
    ;
  },

  'Should also see fields if benefits=no but dependants=yes': function(client) {
    client
      .startService()
      .scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes'])
      .interstitialPage()
      .aboutSetAllToNo(false, {
        'have_dependants': 1
      })
      .setValue('input[name="num_dependants"]', 1)
      .submitForm('form')
      .waitForElementVisible(income_page_sentinel, 5000,
        'Income page should show')
      .waitForElementVisible('[name="your_income-child_tax_credit-per_interval_value"]', 5000,
        'Child tax credits should be present')
    ;
    client.end();
  }

};
