'use strict';

var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Additional Benefits page…');

    client
      .assert.urlContains('/additional-benefits',
        '  - Additional Benefits page URL is correct')
      .click('input[name="other_benefits"][value="0"]', function() {
        console.log('     • Other benefits is ‘No’');
      })
      .conditionalFormSubmit(true, shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
