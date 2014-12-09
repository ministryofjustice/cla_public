'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var SAVINGS_THRESHOLD = require('../modules/constants').SAVINGS_THRESHOLD;
var SAVINGS_QUESTIONS = require('../modules/constants').SAVINGS_QUESTIONS;
SAVINGS_QUESTIONS.ALL = SAVINGS_QUESTIONS.MONEY.concat(SAVINGS_QUESTIONS.VALUABLES);

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    client
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'have_savings', 1);
    client.submitForm('form');
  },

  'Savings page': function(client) {
    client
      .assert.urlContains('/savings')
      .assert.containsText('h1', 'Your savings')
    ;
  },

  'Context-dependent text for partner': function(client) {
    client
      .assert.containsText('body', 'We need to know about any money you have saved or invested.')
      .back();
    common.setYesNoFields(client, 'have_partner', 1);
    common.setYesNoFields(client, 'in_dispute', 0);
    common.setYesNoFields(client, ['partner_is_employed', 'partner_is_self_employed'], 0);
    client
      .submitForm('form')
      .assert.urlContains('/savings')
      .assert.containsText('h1', 'You and your partner’s savings')
      .assert.containsText('body', 'Any cash, savings or investments held in both your names.')
    ;
  },

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

    SAVINGS_QUESTIONS.MONEY.forEach(function(item) {
      common.submitAndCheckForFieldError(client, item.name, item.errorText);
    });
    SAVINGS_QUESTIONS.VALUABLES.forEach(function(item) {
      client.assert.hidden(util.format('input[name="%s"]', item.name));
    });
    client
      .url(client.launch_url + '/about')
      .assert.urlContains('/about')
    ;
    common.setYesNoFields(client, 'have_valuables', 1);
    common.setYesNoFields(client, 'have_savings', 0);
    client.submitForm('form');
    SAVINGS_QUESTIONS.VALUABLES.forEach(function(item) {
      common.submitAndCheckForFieldError(client, item.name, item.errorText);
    });
    SAVINGS_QUESTIONS.MONEY.forEach(function(item) {
      client.assert.hidden(util.format('input[name="%s"]', item.name));
    });
  },

  'Test outcomes': function(client) {
    client.url(client.launch_url + '/about');
    common.setYesNoFields(client, 'have_valuables', 1);
    common.setYesNoFields(client, 'have_savings', 1);
    client.submitForm('form');
    common.setAllSavingsFieldsToValue(client, 500);
    client
      .submitForm('form')
      .assert.urlContains('/income', 'Should arrive at income page when all savings/money fields set to £500')
      .back()
    ;

    SAVINGS_QUESTIONS.ALL.forEach(function(item) {
      // set all to 0
      common.setAllSavingsFieldsToValue(client, 0);
      // set this item to SAVINGS_THRESHOLD
      client
        .setValue(util.format('input[name="%s"]', item.name), SAVINGS_THRESHOLD)
        .submitForm('form')
        .assert.urlContains('/income', util.format('Should arrive at income page when %s field set to %s and others to £0', item.name, SAVINGS_THRESHOLD))
        .back()
      ;
    });



    SAVINGS_QUESTIONS.ALL.forEach(function(item) {
      // start from scratch because result pages clear session
      common.startPage(client);
      common.selectDebtCategory(client);
      common.aboutPageSetAllToNo(client);
      common.setYesNoFields(client, ['have_savings', 'have_valuables'], 1);
      client.submitForm('form');
      // set all to 0
      common.setAllSavingsFieldsToValue(client, 0);
      // set this item to SAVINGS_THRESHOLD+1
      client
        .setValue(util.format('input[name="%s"]', item.name), SAVINGS_THRESHOLD + 1)
        .submitForm('form')
        .assert.urlContains('/help-organisations', util.format('Result ineligible when %s field set to £%s', item.name, (SAVINGS_THRESHOLD + 1)))
      ;
    });

    client.end();
  }
};
