'use strict';

var util = require('util');
var common = require('../modules/common-functions');

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

  'Child benefit fields': function(client) {
    client
      .assert.hidden('input[name="child_benefit-amount"]')
      .back()
      .back()
    ;
    common.setYesNoFields(client, 'have_children', 1);
    client
      .setValue('[name="num_children"]', 1)
      .submitForm('form')
      .assert.containsText('h1', 'Your benefits')
    ;


    client.end();
  }

};
