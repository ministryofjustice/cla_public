'use strict';

var common = require('../../modules/common-functions');

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': function(client) {
    client
      .assert.urlContains('/problem')
      .assert.containsText('h1', 'What do you need help with?')
      .click('input[name="categories"][value="clinneg"]')
      .assert.attributeEquals('input[name="categories"][value="clinneg"]', 'checked', 'true')
      .submitForm('form')
    ;
  },

  'Face-to-face page': function(client) {
    client
      .waitForElementVisible('.legal-adviser-search', 5000)
      .assert.urlContains('/face-to-face')
      .assert.containsText('h1', 'You may be able to get free advice from a legal adviser')
    ;
  },

  'Find legal adviser search': function(client) {
    client
      .setValue('input[name="postcode"]', 'w22dd')
      .submitForm('form')
      .assert.urlContains('/face-to-face')
      .waitForElementVisible('.search-results-container', 5000)
      .assert.containsText('.results-location', 'W2 2DD')
    ;

    client.end();
  }

};
