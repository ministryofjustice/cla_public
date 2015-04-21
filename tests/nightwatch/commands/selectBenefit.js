'use strict';

var log = require('../modules/log');

exports.command = function(benefitFieldName, shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Benefits page…');

    client
      .assert.urlContains('/benefits',
        '  - Benefits page URL is correct')
      .click('input[name="benefits"][value="' + benefitFieldName +'"]', function() {
        console.log('     • Options selected ‘' + benefitFieldName + '’');
      })
      .conditionalFormSubmit(shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
