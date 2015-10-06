'use strict';

var ABOUT_YOU_QUESTIONS = require('../modules/constants').ABOUT_YOU_QUESTIONS;
var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing About you page...');

    client
      .ensureCorrectPage('#have_partner-0', '/about', {
        'h1': 'About you'
      })
      .setYesNoFields(ABOUT_YOU_QUESTIONS, 1, function() {
        console.log('     • Setting all values to ‘Yes’');
      })
      .click('input[name="in_dispute"][value="0"]', function() {
        console.log('     • In dispute with partner set to ‘No’');
      })
      .setValue('input[name="num_children"]', 2, function() {
        console.log('     • Number of children set to 2');
      })
      .setValue('input[name="num_dependants"]', 1, function() {
        console.log('     • Number of dependants set to 1');
      })
      .click('input[name="partner_is_employed"][value="1"]', function() {
        console.log('     • Is partner employed set to ‘Yes’');
      })
      .click('input[name="partner_is_self_employed"][value="0"]', function() {
        console.log('     • Is partner self-employed set to ‘No’');
      })
      .conditionalFormSubmit(shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
