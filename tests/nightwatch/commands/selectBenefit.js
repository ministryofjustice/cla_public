'use strict';

var log = require('../modules/log');

exports.command = function(benefitFieldName, shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Benefits page...');

    client
      .ensureCorrectPage('body.js-enabled', '/benefits')
      .click('input[name="benefits"][value="' + benefitFieldName +'"]', function() {
        console.log('     • Option clicked ‘' + benefitFieldName + '’');
      })
      .conditionalFormSubmit(shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
