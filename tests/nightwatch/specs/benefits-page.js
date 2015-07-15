'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var constants = require('../modules/constants');
var BENEFITS = constants.BENEFITS;

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis(constants.SCOPE_PATHS.debtInScope);
  },

  'Interstitial page': function(client) {
    client.interstitialPage();
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true, {
      'on_benefits': 1
    });
  },

  'Benefits': function(client) {
    client
      .waitForElementVisible('input[name="benefits"]', 5000)
      .assert.urlContains('/benefits')
      .assert.containsText('h1', 'Your benefits')
      .assert.containsText('body', 'Which benefits do you receive?')
    ;
  },

  'Context-dependent text and headline for partner': function(client) {
    client
      .assert.doesNotContainText('h1', 'You and your partner’s benefits')
      .assert.doesNotContainText('body', 'Which benefits do you and your partner receive?')
      .back()
      .waitForElementVisible('input[name="have_partner"]', 5000)
      .setYesNoFields('have_partner', 1)
      .setYesNoFields(['in_dispute', 'partner_is_employed', 'partner_is_self_employed'], 0)
      .submitForm('form')
      .waitForElementVisible('input[name="benefits"]', 5000)
      .assert.containsText('h1', 'You and your partner’s benefits')
      .assert.containsText('body', 'Which benefits do you and your partner receive?')
    ;
  },

  'Test validation': function(client) {
    client.submitForm('form');
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');
  },

  'Test outcomes': function(client) {
    BENEFITS.forEach(function(item) {
      var destination = (item === 'other-benefit' ? '/additional-benefits' : '/review');
      var waitElement = (item === 'other-benefit' ? 'input[name="other_benefits"]' : '.answers-summary');
      client
        .click(util.format('input[value="%s"]', item))
        .submitForm('form')
        .waitForElementVisible(waitElement, 5000)
        .assert.urlContains(destination, util.format('Goes to %s when %s is checked', destination, item))
        .url(client.launch_url + '/benefits')
        .waitForElementVisible('input[name="benefits"]', 5000)
        .click(util.format('input[value="%s"]', item))
      ;
    });

    client.end();
  }

};
