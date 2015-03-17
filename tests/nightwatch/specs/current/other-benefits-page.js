'use strict';

var util = require('util');
var common = require('../../modules/common-functions');
var CHILD_BENEFIT_QUESTIONS = require('../../modules/constants').CHILD_BENEFIT_QUESTIONS;

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    common.aboutPage(client);
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'on_benefits', 1);
    client.submitForm('form');
  },

  'Benefits': function(client) {
    client
      .waitForElementVisible('input[name="benefits"]', 5000)
      .assert.urlContains('/benefits')
      .assert.containsText('h1', 'Your benefits')
      .assert.containsText('body', 'Are you on any of these benefits?')
      .click('input[value="other-benefit"]')
      .submitForm('form')
    ;
  },

  'Benefits and tax credits page': function(client) {
    client
      .waitForElementVisible('input[name="other_benefits"]', 5000)
      .assert.urlContains('/benefits-tax-credits')
    ;
    common.checkTextIsEqual(client, 'h1', 'Your benefits and tax credits');
  },

  'Context-dependent text for partner': function(client) {
    client
      .back()
      .waitForElementPresent('input[name="benefits"]', 5000)
      .back()
      .waitForElementPresent('input[name="have_partner"]', 5000)
    ;
    common.setYesNoFields(client, 'have_partner', 1);
    common.setYesNoFields(client, 'in_dispute', 0);
    common.setYesNoFields(client, ['partner_is_employed', 'partner_is_self_employed'], 0);
    client
      .submitForm('form')
      .waitForElementPresent('input[name="benefits"]', 5000)
      .submitForm('form')
      .waitForElementPresent('input[name="other_benefits"]', 5000)
    ;
    common.checkTextIsEqual(client, 'h1', 'You and your partner’s benefits and tax credits');
  },

  'Child benefit fields': function(client) {
    CHILD_BENEFIT_QUESTIONS.forEach(function(item) {
      client.assert.hidden(util.format('input[name="%s-per_interval_value"]', item));
      client.assert.hidden(util.format('input[name="%s-interval_period"]', item));
    });
    client
      .back()
      .waitForElementPresent('input[name="benefits"]', 5000)
      .back()
      .waitForElementPresent('input[name="have_partner"]', 5000)
    ;
    common.setYesNoFields(client, 'have_children', 1);
    client
      .setValue('input[name="num_children"]', 1)
      .submitForm('form')
      .waitForElementPresent('input[name="benefits"]', 5000)
      .submitForm('form')
      .waitForElementPresent('input[name="other_benefits"]', 5000)
    ;
    CHILD_BENEFIT_QUESTIONS.forEach(function(item) {
      client.assert.visible(util.format('input[name="%s-per_interval_value"]', item));
      client.assert.visible(util.format('select[name="%s-interval_period"]', item));
    });
  },

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

    CHILD_BENEFIT_QUESTIONS.forEach(function(item) {
      client
        .setValue(util.format('input[name="%s-per_interval_value"]', item), '100')
      ;
      common.submitAndCheckForFieldError(client, item + '-per_interval_value', 'Please select a time period from the drop down');
      client
        .clearValue(util.format('input[name="%s-per_interval_value"]', item))
        .click(util.format('select[name="%s-interval_period"]', item))
        .click(util.format('select[name="%s-interval_period"] option:first-child + option', item))
      ;
      common.submitAndCheckForFieldError(client, item + '-interval_period', 'Not a valid amount', 'select');
      client
        .setValue(util.format('input[name="%s-per_interval_value"]', item), '100')
      ;
    });

    common.submitAndCheckForFieldError(client, 'other_benefits', 'Please choose Yes or No');
    client.click('input[name="other_benefits"][value="1"]');
    common.submitAndCheckForFieldError(client, 'other_benefits', 'Please provide an amount');
    client.setValue('input[name="total_other_benefit-per_interval_value"]', '100');
    common.submitAndCheckForFieldError(client, 'other_benefits', 'Please select a time period from the drop down');
    client
      .clearValue('input[name="total_other_benefit-per_interval_value"]')
      .click('select[name="total_other_benefit-interval_period"]')
      .click('select[name="total_other_benefit-interval_period"] option:first-child + option')
    ;
    common.submitAndCheckForFieldError(client, 'other_benefits', 'Not a valid amount');
    client
      .setValue('input[name="total_other_benefit-per_interval_value"]', '100')
      .submitForm('form')
      .waitForElementPresent('input[name="your_income-other_income-per_interval_value"]', 5000)
      .assert.urlContains('/income')
    ;
  },

  'Should also see page if benefits=no but children=yes': function(client) {
    common.startPage(client);
    common.selectDebtCategory(client);

    client
      .waitForElementPresent('input[name="have_partner"]', 5000)
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'have_children', 1);
    client
      .setValue('input[name="num_children"]', 1)
      .submitForm('form')
      .waitForElementPresent('input[name="other_benefits"]', 5000)
      .assert.urlContains('/benefits-tax-credits')
    ;

  },

  'Should also see page if benefits=no but dependants=yes': function(client) {
    common.startPage(client);
    common.selectDebtCategory(client);

    client
      .waitForElementPresent('input[name="have_partner"]', 5000)
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'have_dependants', 1);
    client
      .setValue('input[name="num_dependants"]', 1)
      .submitForm('form')
      .waitForElementPresent('input[name="other_benefits"]', 5000)
      .assert.urlContains('/benefits-tax-credits')
    ;

    client.end();
  }

};
