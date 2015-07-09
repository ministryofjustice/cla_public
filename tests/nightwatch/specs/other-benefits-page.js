'use strict';

var util = require('util');
var common = require('../modules/common-functions');

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes']);
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true, {
      'on_benefits': 1
    });
  },

  'Benefits': function(client) {
    client.selectBenefit('other-benefit', true);
  },

  'Additional Benefits page': function(client) {
    client
      .waitForElementVisible('input[name="other_benefits"]', 5000)
      .assert.urlContains('/additional-benefits')
    ;
    common.checkTextIsEqual(client, 'h1', 'Your additional benefits');
  },

  'Context-dependent text for partner': function(client) {
    client
      .back()
      .waitForElementPresent('input[name="benefits"]', 5000)
      .back()
      .waitForElementPresent('input[name="have_partner"]', 5000)
      .setYesNoFields('have_partner', 1)
      .setYesNoFields(['in_dispute', 'partner_is_employed', 'partner_is_self_employed'], 0)
      .submitForm('form')
      .waitForElementPresent('input[name="benefits"]', 5000)
      .submitForm('form')
      .waitForElementPresent('input[name="other_benefits"]', 5000)
    ;
    common.checkTextIsEqual(client, 'h1', 'You and your partner’s additional benefits');
  },

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

    common.submitAndCheckForFieldError(client, [{
      name: 'other_benefits',
      errorText: 'Please choose Yes or No'
    }]);
    client.click('input[name="other_benefits"][value="1"]');
    common.submitAndCheckForFieldError(client, [{
      name: 'other_benefits',
      errorText: 'Please provide an amount'
    }]);
    client.setValue('input[name="total_other_benefit-per_interval_value"]', '100');
    common.submitAndCheckForFieldError(client, [{
      name: 'other_benefits',
      errorText: 'Please select a time period from the drop down'
    }]);
    client
      .clearValue('input[name="total_other_benefit-per_interval_value"]')
      .click('select[name="total_other_benefit-interval_period"]')
      .click('select[name="total_other_benefit-interval_period"] option:first-child + option')
    ;
    common.submitAndCheckForFieldError(client, [{
      name: 'other_benefits',
      errorText: 'Please provide an amount'
    }]);
    client
      .setValue('input[name="total_other_benefit-per_interval_value"]', '100')
      .submitForm('form')
      .waitForElementPresent('input[name="your_income-other_income-per_interval_value"]', 5000)
      .assert.urlContains('/income')
    ;
  }

};
