'use strict';

var common = require('../../modules/common-functions');

module.exports = {
  'Start page': common.startPage,

  'Scope diagnosis': common.selectDebtCategory,

  'About you': function(client) {
    client
      .waitForElementVisible('a.continue', 5000)
      .click('a.continue')
      .waitForElementVisible('input[name="have_partner"]', 5000)
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;
    common.aboutPageSetAllToNo(client);
    client
      .submitForm('form')
      .end()
    ;
  },

  'Start page again': function(client) {
    // not using common.startPage because that clears cookies which would negate this test
    client
      .init()
      .maximizeWindow()
      .waitForElementVisible('body', 1000)
      .click('a#start')
    ;
  },

  'Scope diagnosis again': common.selectDebtCategory,

  'Check option is not selected': function(client) {
    client
      .waitForElementVisible('a.continue', 5000)
      .click('a.continue')
      .waitForElementVisible('input[name="have_partner"]', 5000)
      .assert.urlContains('/about')
    ;
    common.checkAttributeIsNotPresent(client, 'input[name="have_partner"]', 'checked');

    client.end();
  }

};
