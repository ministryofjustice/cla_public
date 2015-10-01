'use strict';

var log = require('../modules/log');

exports.command = function() {
  var client = this;

  this.perform(function() {
    log.command('Passing interstitial page...');

    client
      .ensureCorrectPage('body.js-enabled', '/legal-aid-available')
      .click('a.button-get-started', function() {
        console.log('     ⟡ `Check if you qualify financially` clicked');
      })
      .ensureCorrectPage('body.js-enabled', '/about')
    ;
  });

  return client;
};
