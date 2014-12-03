'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var SAVINGS_QUESTIONS = require('../modules/constants').SAVINGS_QUESTIONS;

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
    client
      .submitForm('form')
      .assert.urlContains('/savings')
      .assert.containsText('h1', 'You and your partner’s savings')
      .assert.containsText('body', 'Any cash, savings or investments held in both your names.')
    ;
  },

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

    SAVINGS_QUESTIONS.forEach(function(item) {
      common.submitAndCheckForFieldError(client, item.name, item.errorText);
    });
  },

  'Test outcomes': function(client) {
    SAVINGS_QUESTIONS.forEach(function(item) {
      client
        .clearValue(util.format('input[name="%s"]', item.name))
        .setValue(util.format('input[name="%s"]', item.name), '500')
      ;
    });
    client
      .submitForm('form')
      .assert.urlContains('/income', 'Should arrive at income page when all savings fields set to £500')
      .back()
    ;
    SAVINGS_QUESTIONS.forEach(function(item) {
      client.setValue(util.format('input[name="%s"]', item.name), '5000');
    });
    client
      .submitForm('form')
      .assert.urlContains('/result/ineligible', 'Result ineligible when all savings fields set to £5000')
    ;

    client.end();
  }
};
