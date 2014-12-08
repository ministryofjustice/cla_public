'use strict';

var common = require('../modules/common-functions');

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    client
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
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

  'Check debt category NOT selected': function(client) {
    client.assert.urlContains('/problem');
    common.checkAttributeIsNotPresent(client, 'input[name="categories"][value="debt"]', 'checked');

    client.end();
  }

};
