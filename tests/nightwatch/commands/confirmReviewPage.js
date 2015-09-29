'use strict';

var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Review Answers page...');

    client
      .ensureCorrectPage('.answers-summary', '/review', {
        'h1': 'Review your answers'
      })
      .conditionalFormSubmit(true)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
