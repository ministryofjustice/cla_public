'use strict';

var constants = require('../modules/constants');

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis(constants.SCOPE_PATHS.clinnegFaceToFace);
  },

  'Face-to-face page': function(client) {
    client
      .waitForElementVisible('.legal-adviser-search', 5000)
      .assert.urlContains('/scope/refer/legal-adviser')
      .assert.containsText('h1', 'A legal adviser may be able to help you')
      .checkFlashMessage()
    ;
  },

  'Find legal adviser search': function(client) {
    client
      .setValue('input[name="postcode"]', 'w22dd')
      .submitForm('form')
      .assert.urlContains('/scope/refer/legal-adviser')
      .waitForElementVisible('.search-results-container', 5000)
      .assert.containsText('.results-summary', 'results around')
      .assert.containsText('.results-filter', constants.SCOPE_PATHS.clinnegFaceToFace.title.toUpperCase())
    ;

    client.end();
  }

};
