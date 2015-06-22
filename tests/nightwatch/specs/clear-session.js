'use strict';

var common = require('../modules/common-functions');

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes']);
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true);
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

  'Scope diagnosis again': function(client) {
    client.scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes']);
  },

  'Check option is not selected': function(client) {
    common.checkAttributeIsNotPresent(client, 'input[name="have_partner"]', 'checked');

    client.end();
  }

};
