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

  'Savings': function(client) {
    // test context-dependent text for partner
    client
      .assert.urlContains('/savings')
      .assert.containsText('h1', 'Your savings')
    ;
    common.checkTextIsEqual(client, 'label[for="valuables"]', 'Valuable items you own worth over £500 each');
    client.back();
    common.setYesNoFields(client, 'have_partner', 1);
    client
      .submitForm('form')
      .assert.urlContains('/savings')
      .assert.containsText('h1', 'You and your partner’s savings')
    ;
    common.checkTextIsEqual(client, 'label[for="valuables"]', 'Valuable items you and your partner own worth over £500 each');

    // test validation
    common.submitAndCheckForError(client, 'This form has errors.\nPlease correct them and try again.');

    SAVINGS_QUESTIONS.forEach(function(item) {
      common.submitAndCheckForFieldError(client, item, 'Not a valid amount');
    });

    // check outcomes
    SAVINGS_QUESTIONS.forEach(function(item) {
      client.setValue(util.format('input[name="%s"]', item), '5000');
    });
    client
      .submitForm('form')
      .verify.urlContains('/result/ineligible', 'Result ineligible when all savings fields set to £5000')
      .back()
    ;
    SAVINGS_QUESTIONS.forEach(function(item) {
      client
        .clearValue(util.format('input[name="%s"]', item))
        .setValue(util.format('input[name="%s"]', item), '500')
      ;
    });
    client
      .submitForm('form')
      .verify.urlContains('/income', 'Should arrive at income page when all savings fields set to £500')
    ;

    client.end();
  }

};
