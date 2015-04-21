'use strict';

var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Savings page…');

    client
      .assert.urlContains('/savings',
        '  - Savings page URL is correct')
      .setValue('input[name="savings"]', 1000, function() {
        console.log('     • Savings is £1,000');
      })
      .setValue('input[name="investments"]', 1000, function() {
        console.log('     • Investments is £1,000');
      })
      .setValue('input[name="valuables"]', 1000, function() {
        console.log('     • Valuables is £1,000');
      })
      .conditionalFormSubmit(shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
