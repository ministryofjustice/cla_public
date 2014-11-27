'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var CHILD_BENEFIT_QUESTIONS = require('../modules/constants').CHILD_BENEFIT_QUESTIONS;

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    client
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'on_benefits', 1);
    client.submitForm('form');
  },

  'Benefits': function(client) {
    client
      .assert.urlContains('/benefits')
      .assert.containsText('h1', 'Your benefits')
      .assert.containsText('body', 'Are you on any of these benefits?')
      .click('input[value="other-benefit"]')
      .submitForm('form')
    ;
  },

  'Benefits and tax credits page': function(client) {
    client
      .assert.urlContains('/benefits-tax-credits')
    ;
    common.checkTextIsEqual(client, 'h1', 'Your benefits and tax credits');
  },

  'Context-dependent text for partner': function(client) {
    client
      .back()
      .back()
    ;
    common.setYesNoFields(client, 'have_partner', 1);
    client
      .submitForm('form')
      .click('input[value="other-benefit"]')
      .submitForm('form')
    ;
    common.checkTextIsEqual(client, 'h1', 'You and your partner’s benefits and tax credits');
  },

  'Child benefit fields': function(client) {
    CHILD_BENEFIT_QUESTIONS.forEach(function(item) {
      client.assert.hidden(util.format('input[name="%s-amount"]', item));
      client.assert.hidden(util.format('input[name="%s-interval"]', item));
    });
    client
      .back()
      .back()
    ;
    common.setYesNoFields(client, 'have_children', 1);
    client
      .setValue('input[name="num_children"]', 1)
      .submitForm('form')
      .click('input[value="other-benefit"]')
      .submitForm('form')
    ;
    CHILD_BENEFIT_QUESTIONS.forEach(function(item) {
      client.assert.visible(util.format('input[name="%s-amount"]', item));
      client.assert.visible(util.format('select[name="%s-interval"]', item));
    });
  },

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

    CHILD_BENEFIT_QUESTIONS.forEach(function(item) {
      client
        .setValue(util.format('input[name="%s-amount"]', item), '100')
      ;
      common.submitAndCheckForFieldError(client, item + '-amount', 'Please select a time period from the drop down');
      client
        .clearValue(util.format('input[name="%s-amount"]', item))
        .setValue(util.format('select[name="%s-interval"]', item), 'per month')
      ;
      common.submitAndCheckForFieldError(client, item + '-interval', 'Not a valid amount', 'select');
      client
        .setValue(util.format('input[name="%s-amount"]', item), '100')
      ;
    });

    common.submitAndCheckForFieldError(client, 'other_benefits', 'Please choose Yes or No');
    client.click('input[name="other_benefits"][value="1"]');
    common.submitAndCheckForFieldError(client, 'other_benefits', 'Please provide an amount');
    client.setValue('input[name="total_other_benefit-amount"]', '100');
    common.submitAndCheckForFieldError(client, 'other_benefits', 'Please select a time period from the drop down');
    client
      .clearValue('input[name="total_other_benefit-amount"]')
      .setValue('select[name="total_other_benefit-interval"]', 'per month')
    ;
    common.submitAndCheckForFieldError(client, 'other_benefits', 'Not a valid amount');
    client
      .setValue('input[name="total_other_benefit-amount"]', '100')
      .submitForm('form')
      .assert.urlContains('/income')
    ;

    client.end();
  }

};
