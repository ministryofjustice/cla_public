'use strict';

var constants = require('../modules/constants');

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  '@disabled': true,
  'Scope diagnosis': function(client) {
    client.scopeDiagnosis(constants.SCOPE_PATHS.clinnegFaceToFace);
  },

  'Face-to-face page': function(client) {
    client
      .ensureCorrectPage('.legal-adviser-search', '/scope/refer/legal-adviser', {
        'h1': 'A legal adviser may be able to help you'
      })
     .checkFlashMessage()
    ;
  },

  'Find legal adviser search': function(client) {
    client
      .setValue('input[name="postcode"]', 'w22dd', function() {
        console.log('     • Enter postcode `w22dd`');
      })
      .conditionalFormSubmit(true)
      .assert.urlContains('/scope/refer/legal-adviser',
        '    - Page is ready'
      )
      .waitForElementVisible('.search-results-container', 5000,
        '    - Search results are shown'
      )
      .assert.containsText('.results-summary', 'results around',
        '    - Results summary has location'
      )
      .assert.containsText('.results-filter', constants.SCOPE_PATHS.clinnegFaceToFace.title.toUpperCase(),
        '    - Filter contains category name'
      )
    ;

    client.end();
  }

};
