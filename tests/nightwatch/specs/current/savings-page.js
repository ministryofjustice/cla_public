'use strict';

var util = require('util');
var common = require('../../modules/common-functions');
var VALUABLES_MINIMUM = require('../../modules/constants').VALUABLES_MINIMUM;
var SAVINGS_THRESHOLD = require('../../modules/constants').SAVINGS_THRESHOLD;
var SAVINGS_QUESTIONS = require('../../modules/constants').SAVINGS_QUESTIONS;
SAVINGS_QUESTIONS.ALL = SAVINGS_QUESTIONS.MONEY.concat(SAVINGS_QUESTIONS.VALUABLES);

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    common.aboutPage(client);
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'have_savings', 1);
    client.submitForm('form');
  },

  'Savings page': function(client) {
    client
      .waitForElementVisible('input[name="savings"]', 5000)
      .assert.urlContains('/savings')
      .assert.containsText('h1', 'Your savings')
    ;
  },

  'Context-dependent text for partner': function(client) {
    client
      .assert.containsText('body', 'We need to know about any money you have saved or invested.')
      .back()
      .waitForElementVisible('input[name="have_partner"]', 5000)
    ;
    common.setYesNoFields(client, 'have_partner', 1);
    common.setYesNoFields(client, 'in_dispute', 0);
    common.setYesNoFields(client, ['partner_is_employed', 'partner_is_self_employed'], 0);
    client
      .submitForm('form')
      .waitForElementVisible('input[name="savings"]', 5000)
      .assert.urlContains('/savings')
      .assert.containsText('h1', 'You and your partner’s savings')
      .assert.containsText('body', 'Any cash, savings or investments held in your name, your partner’s name or both your names')
    ;
  },

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

    var questions = [];
    SAVINGS_QUESTIONS.MONEY.forEach(function(item) {
      questions.push({
        name: item.name,
        errorText: item.errorText
      });
    });
    common.submitAndCheckForFieldError(client, questions);
    SAVINGS_QUESTIONS.VALUABLES.forEach(function(item) {
      client.assert.elementNotPresent(util.format('input[name="%s"]', item.name));
    });
    client.end();
  },

  'More validation': function(client) {
    common.startPage(client);
    common.selectDebtCategory(client);
    common.aboutPage(client);
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'have_valuables', 1);
    client
      .submitForm('form')
      .waitForElementVisible('input[name="valuables"]', 5000)
    ;
    var questions = [];
    SAVINGS_QUESTIONS.VALUABLES.forEach(function(item) {
      questions.push({
        name: item.name,
        errorText: item.errorText
      });
    });
    common.submitAndCheckForFieldError(client, questions);
    SAVINGS_QUESTIONS.MONEY.forEach(function(item) {
      client.assert.elementNotPresent(util.format('input[name="%s"]', item.name));
    });
    client.end();
  },

  'Test outcomes': function(client) {
    common.startPage(client);
    common.selectDebtCategory(client);
    common.aboutPage(client);
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, ['have_valuables', 'have_savings'], 1);
    client
      .submitForm('form')
      .waitForElementVisible('input[name="savings"]', 5000)
    ;
    common.setAllSavingsFieldsToValue(client, 501);
    client
      .submitForm('form')
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000)
      .assert.urlContains('/income', 'Should arrive at income page when all savings/money fields set to £501')
      .back()
      .waitForElementVisible('input[name="savings"]', 5000)
    ;

    SAVINGS_QUESTIONS.ALL.forEach(function(item) {
      // set all to 0
      common.setAllSavingsFieldsToValue(client, 0);
      // set this item to SAVINGS_THRESHOLD
      if(item.name === 'valuables') {
        client
          .clearValue(util.format('input[name="%s"]', item.name))
          .setValue(util.format('input[name="%s"]', item.name), SAVINGS_THRESHOLD)
        ;
      } else {
        client
          .clearValue('input[name="valuables"]')
          .clearValue(util.format('input[name="%s"]', item.name))
          .setValue('input[name="valuables"]', VALUABLES_MINIMUM)
          .setValue(util.format('input[name="%s"]', item.name), SAVINGS_THRESHOLD - VALUABLES_MINIMUM)
        ;
      }
      client
        .submitForm('form')
        .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000)
        .assert.urlContains('/income', util.format('Should arrive at income page when %s field set to %s and others to £0', item.name, SAVINGS_THRESHOLD))
        .back()
        .waitForElementVisible('input[name="savings"]', 5000)
      ;
    });



    SAVINGS_QUESTIONS.ALL.forEach(function(item) {
      // start from scratch because result pages clear session
      common.startPage(client);
      common.selectDebtCategory(client);
      common.aboutPageSetAllToNo(client);
      common.setYesNoFields(client, ['have_savings', 'have_valuables'], 1);
      client
        .submitForm('form')
        .waitForElementVisible('input[name="savings"]', 5000)
      ;
      // set all to 0
      common.setAllSavingsFieldsToValue(client, 0);
      // set this item to SAVINGS_THRESHOLD+1
      if(item.name === 'valuables') {
        client
          .clearValue(util.format('input[name="%s"]', item.name))
          .setValue(util.format('input[name="%s"]', item.name), SAVINGS_THRESHOLD + 1)
        ;
      } else {
        client
          .clearValue('input[name="valuables"]')
          .clearValue(util.format('input[name="%s"]', item.name))
          .setValue('input[name="valuables"]', VALUABLES_MINIMUM)
          .setValue(util.format('input[name="%s"]', item.name), SAVINGS_THRESHOLD - VALUABLES_MINIMUM + 1)
        ;
      }
      client
        .submitForm('form')
        .waitForElementVisible('.answers-summary', 5000)
        .submitForm('form')
        .waitForElementVisible('a[href="https://www.gov.uk/find-a-legal-adviser"]', 5000)
        .assert.urlContains('/help-organisations', util.format('Result ineligible when %s field set to £%s', item.name, (SAVINGS_THRESHOLD + 1)))
      ;
    });

    client.end();
  }
};
