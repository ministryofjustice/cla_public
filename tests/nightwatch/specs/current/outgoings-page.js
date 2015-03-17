'use strict';

var util = require('util');
var common = require('../../modules/common-functions');
var OUTGOINGS_QUESTIONS = require('../../modules/constants').OUTGOINGS_QUESTIONS;

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    common.aboutPage(client);
    common.aboutPageSetAllToNo(client);
    client.submitForm('form');
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
      .assert.hidden('input[name="childcare-per_interval_value"]')
      .assert.hidden('input[name="childcare-interval_period"]')
      .back()
      .waitForElementPresent('input[name="your_income-other_income-per_interval_value"]', 5000)
      .back()
      .waitForElementPresent('input[name="have_partner"]', 5000)
    ;
    common.setYesNoFields(client, 'have_children', 1);
    client
      .setValue('input[name="num_children"]', 1)
      .submitForm('form')
      .waitForElementVisible('input[name="other_benefits"]', 5000)
    ;
    common.setYesNoFields(client, 'other_benefits', 0);
    client
      .setValue('input[name="child_benefit-per_interval_value"]', 0)
      .setValue('input[name="child_tax_credit-per_interval_value"]', 0)
      .submitForm('form')
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000)
      .clearValue('input[name="your_income-maintenance-per_interval_value"]')
      .clearValue('input[name="your_income-pension-per_interval_value"]')
      .clearValue('input[name="your_income-other_income-per_interval_value"]')
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
      .waitForElementVisible('input[name="other_benefits"]', 5000)
      .back()
      .waitForElementPresent('input[name="have_partner"]', 5000)
    ;
    common.setYesNoFields(client, 'have_partner', 1);
    common.setYesNoFields(client, 'in_dispute', 0);
    common.setYesNoFields(client, ['partner_is_employed', 'partner_is_self_employed'], 0);
    client
      .submitForm('form')
      .waitForElementPresent('input[name="other_benefits"]', 5000)
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
      common.submitAndCheckForFieldError(client, item + '-per_interval_value', 'Please select a time period from the drop down');
      client.clearValue(util.format('input[name=%s-per_interval_value]', item));
      common.setDropdownValue(client, item + '-interval_period', 'per_month');
      common.submitAndCheckForFieldError(client, item + '-per_interval_value', 'Not a valid amount');
    });

    common.submitAndCheckForFieldError(client, 'income_contribution', 'Not a valid amount');

    OUTGOINGS_QUESTIONS.forEach(function(item) {
      client.setValue(util.format('input[name=%s-per_interval_value]', item), '500');
    });
    client
      .setValue('input[name="income_contribution"]', 0)
      .submitForm('form')
      .waitForElementPresent('input[name="callback-contact_number"]', 5000)
      .assert.urlContains('/result/eligible')
    ;

    client.end();
  }

};
