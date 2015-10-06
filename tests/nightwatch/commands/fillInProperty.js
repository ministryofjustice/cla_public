'use strict';

var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Property page...');

    client
      .ensureCorrectPage('body.js-enabled', '/property')
      .click('input[name="properties-0-is_main_home"][value="1"]', function() {
        console.log('     • Selected main property is ‘Yes’');
      })
      .click('input[name="properties-0-other_shareholders"][value="0"]', function() {
        console.log('     • Other sharedholders is ‘No’');
      })
      .setValue('input[name="properties-0-property_value"]', 150000, function() {
        console.log('     • Value is £150,000');
      })
      .setValue('input[name="properties-0-mortgage_remaining"]', 120000, function() {
        console.log('     • Mortgage remaining is £120,000');
      })
      .setValue('input[name="properties-0-mortgage_payments"]', 450, function() {
        console.log('     • Mortgage repayments is £450 last month');
      })
      .click('input[name="properties-0-is_rented"][value="0"]', function() {
        console.log('     • Rent out part of property is ‘No’');
      })
      .click('input[name="properties-0-in_dispute"][value="0"]', function() {
        console.log('     • Property in dispute is ‘No’');
      })
      .conditionalFormSubmit(shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
