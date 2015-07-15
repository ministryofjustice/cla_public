'use strict';

var log = require('../modules/log');

exports.command = function(errorText, callback) {
  var client = this;
  errorText = errorText || 'This form has errors.\nPlease see below for the errors you need to correct.';

  this.perform(function() {
    log.command('Checking form validation…');

    client
      .submitForm('form', function() {
        console.log('     ⟡ Form submitted');
      })
      .waitForElementPresent('.alert-error', 3000, function() {
        console.log('    - Form has errors summary');
      })
      .assert.containsText('.alert-error', errorText)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
