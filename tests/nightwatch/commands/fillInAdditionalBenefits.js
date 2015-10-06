'use strict';

var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Additional Benefits page...');

    client
      .ensureCorrectPage('body.js-enabled', '/additional-benefits')
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
