'use strict';

var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Income page…');

    client
      .assert.urlContains('/outgoings',
        '  - Outgoings page URL is correct')
      .setValue('input[name="rent-per_interval_value"]', 0, function() {
        console.log('     • Rent is £0');
      })
      .setValue('input[name="maintenance-per_interval_value"]', 0, function() {
        console.log('     • Maintenance is £0');
      })
      .setValue('input[name="income_contribution"]', 0, function() {
        console.log('     • Monthly Income Contribution Order is £0');
      })
      .setValue('input[name="childcare-per_interval_value"]', 0, function() {
        console.log('     • Childcare is £0');
      })
      .conditionalFormSubmit(shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
