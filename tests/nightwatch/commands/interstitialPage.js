'use strict';

var log = require('../modules/log');

exports.command = function() {
  var client = this;

  this.perform(function() {
    log.command('Passing interstitial page…');

    client
      .click('a.button-get-started', function() {
        console.log('     ⟡ Start button clicked');
      })
      .assert.urlContains('/about',
        '  - Interstitial page passed');
  });

  return client;
};
