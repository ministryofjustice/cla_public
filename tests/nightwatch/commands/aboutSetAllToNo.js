'use strict';

var ABOUT_YOU_QUESTIONS = require('../modules/constants').ABOUT_YOU_QUESTIONS;
var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing About you page…');

    client
      .setYesNoFields(ABOUT_YOU_QUESTIONS, 0, function() {
        console.log('     • All values set to ‘No’');
      })
      .conditionalFormSubmit(shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
