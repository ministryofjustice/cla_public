'use strict';

var util = require('util');
var common = require('../../modules/common-functions');
var BENEFITS = require('../../modules/constants').BENEFITS;

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
      .waitForElementVisible('input[name="benefits"]', 2000)
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
      .waitForElementVisible('input[name="have_partner"]', 2000)
    ;
    common.setYesNoFields(client, 'have_partner', 1);
    common.setYesNoFields(client, 'in_dispute', 0);
    common.setYesNoFields(client, ['partner_is_employed', 'partner_is_self_employed'], 0);
    client
      .submitForm('form')
      .waitForElementVisible('input[name="benefits"]', 2000)
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
      var destination = (item === 'other-benefit' ? '/benefits-tax-credits' : '/result/eligible');
      var input = (item === 'other-benefit' ? 'other_benefits' : 'callback_requested');
      client
        .click(util.format('input[value="%s"]', item))
        .submitForm('form')
        .waitForElementVisible(util.format('input[name="%s"]', input), 2000)
        .assert.urlContains(destination, util.format('Goes to %s when %s is checked', destination, item))
        .back()
        .waitForElementVisible('input[name="benefits"]', 2000)
        .click(util.format('input[value="%s"]', item))
    });

    client.end();
  }

};
