'use strict';

var log = require('../modules/log');

exports.command = function() {
  var client = this;

  this.perform(function() {
    log.command('Passing interstitial page…');

    client
      .waitForElementPresent('body.js-enabled', 3000, function() {
        console.log('     - Waiting for page to fully load');
      })
      .assert.urlContains('/legal-aid-available',
        '  - Interstitial page URL is correct')
      .click('a.button-get-started', function() {
        console.log('     ⟡ Start button clicked');
      })
      .waitForElementPresent('body.js-enabled', 3000, function() {
        console.log('     - Waiting for page to fully load');
      })
      .assert.urlContains('/about',
        '  - Interstitial page passed')
    ;
  });

  return client;
};
