'use strict';

var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Checking flash message on current page…');

    client
      .assert.elementPresent('.flash-messages',
        '    - Has flash message informing about clearing the session')
      // Refresh page
      .url(function(result) { this.url(result.value); })
      .assert.elementNotPresent('.flash-messages',
        '    - Flash message is gone after refresh')
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
