'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var BENEFITS = require('../modules/constants').BENEFITS;

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
    ;
  },

  'Context-dependent text and headline for partner': function(client) {
    client
      .assert.doesNotContainText('h1', 'You and your partner’s benefits')
      .assert.doesNotContainText('body', 'Are you or your partner on any of these benefits?')
      .back()
    ;
    common.setYesNoFields(client, 'have_partner', 1);
    common.setYesNoFields(client, 'in_dispute', 0);
    client
      .submitForm('form')
      .assert.containsText('h1', 'You and your partner’s benefits')
      .assert.containsText('body', 'Are you or your partner on any of these benefits?')
    ;
  },

  'Test validation': function(client) {
    client.submitForm('form');
    common.submitAndCheckForError(client, 'Please select at least one option.');
  },

  'Test outcomes': function(client) {
    BENEFITS.forEach(function(item) {
      var destination = (item === 'other-benefit' ? '/benefits-tax-credits' : '/eligible');
      client
        .click(util.format('input[value="%s"]', item))
        .submitForm('form')
        .assert.urlContains(destination, util.format('Goes to %s when %s is checked', destination, item))
        .back()
        .click(util.format('input[value="%s"]', item))
    });

    client.end();
  }

};
