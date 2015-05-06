'use strict';

var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Review Answers page…');

    client
      .assert.urlContains('/review',
        '    - Review Answers page URL is correct')
      .conditionalFormSubmit(true)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
