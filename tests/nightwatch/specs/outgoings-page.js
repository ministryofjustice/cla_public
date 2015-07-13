'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var OUTGOINGS_QUESTIONS = require('../modules/constants').OUTGOINGS_QUESTIONS;
var OUTGOINGS_QUESTION_ERRORS = {
  'rent': 'Enter 0 if you don’t pay rent',
  'maintenance': 'Enter 0 if this doesn’t apply to you',
  'childcare': 'Please provide an amount'
};

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
    client.aboutSetAllToNo(true);
  },

  'Income': function(client) {
    client
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000)
      .assert.urlContains('/income')
      .assert.containsText('h1', 'Your money coming in')
      .setValue('input[name="your_income-maintenance-per_interval_value"]', 0)
      .setValue('input[name="your_income-pension-per_interval_value"]', 0)
      .setValue('input[name="your_income-other_income-per_interval_value"]', 0)
      .submitForm('form')
    ;
  },

  'Outgoings': function(client) {
    client
      .waitForElementVisible('input[name="income_contribution"]', 5000)
      .assert.urlContains('/outgoings')
      .assert.containsText('h1', 'Your outgoings')
    ;
  },

  'Childcare fields': function(client) {
    client
      .back()
      .waitForElementPresent('input[name="your_income-other_income-per_interval_value"]', 5000)
      .back()
      .waitForElementPresent('input[name="have_partner"]', 5000)
      .setYesNoFields('have_children', 1)
      .setValue('input[name="num_children"]', 1)
      .submitForm('form')
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000)
      .clearValue('input[name="your_income-maintenance-per_interval_value"]')
      .clearValue('input[name="your_income-pension-per_interval_value"]')
      .clearValue('input[name="your_income-other_income-per_interval_value"]')
      .setValue('input[name="your_income-child_tax_credit-per_interval_value"]', 0)
      .setValue('input[name="your_income-maintenance-per_interval_value"]', 0)
      .setValue('input[name="your_income-pension-per_interval_value"]', 0)
      .setValue('input[name="your_income-other_income-per_interval_value"]', 0)
      .submitForm('form')
      .waitForElementVisible('input[name="income_contribution"]', 5000)
      .assert.visible('input[name="childcare-per_interval_value"]')
      .assert.visible('select[name="childcare-interval_period"]')
    ;
  },

  'Context-dependent text for partner': function(client) {
    client
      .assert.containsText('body', 'Money you pay your landlord')
      .assert.containsText('body', 'Money you pay to an ex-partner for their living costs')
      .assert.containsText('body', 'Money you pay per month towards your criminal legal aid')
      .assert.containsText('body', 'Money you pay for your child to be looked after while you work or study')
      .back()
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000)
      .back()
      .waitForElementPresent('input[name="have_partner"]', 5000)
      .setYesNoFields('have_partner', 1)
      .setYesNoFields(['in_dispute', 'partner_is_employed', 'partner_is_self_employed'], 0)
      .submitForm('form')
      .waitForElementPresent('input[name="your_income-other_income-per_interval_value"]', 5000)

      .setValue('input[name="your_income-maintenance-per_interval_value"]', 0)
      .setValue('input[name="your_income-pension-per_interval_value"]', 0)
      .setValue('input[name="your_income-other_income-per_interval_value"]', 0)
      .setValue('input[name="partner_income-maintenance-per_interval_value"]', 0)
      .setValue('input[name="partner_income-pension-per_interval_value"]', 0)
      .setValue('input[name="partner_income-other_income-per_interval_value"]', 0)

      .submitForm('form')
      .waitForElementPresent('input[name="income_contribution"]', 5000)
      .assert.urlContains('/outgoings')
      .assert.containsText('h1', 'You and your partner’s outgoings')
      .assert.containsText('body', 'Money you and your partner pay your landlord')
      .assert.containsText('body', 'Money you and/or your partner pay to an ex-partner for their living costs')
      .assert.containsText('body', 'Money you and/or your partner pay per month towards your criminal legal aid')
      .assert.containsText('body', 'Money you and your partner pay for your child to be looked after while you work or study')
    ;
  },

  'Validation': function(client) {
    OUTGOINGS_QUESTIONS.forEach(function(item) {
      client.setValue(util.format('input[name=%s-per_interval_value]', item), '500');
      common.submitAndCheckForFieldError(client, [{
        name: item + '-per_interval_value',
        errorText: 'Please select a time period from the drop down'
      }]);
      client.clearValue(util.format('input[name=%s-per_interval_value]', item));
      common.setDropdownValue(client, item + '-interval_period', 'per_month');
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
      .submitForm('form')
      .waitForElementVisible('.answers-summary', 5000)
      .submitForm('form')
      .waitForElementPresent('input[name="callback-contact_number"]', 5000)
      .assert.urlContains('/result/eligible')
    ;

    client.end();
  }

};
