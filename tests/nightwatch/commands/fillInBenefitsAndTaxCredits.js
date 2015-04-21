'use strict';

var log = require('../modules/log');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Benefits and tax credits page…');

    client
      .assert.urlContains('/benefits-tax-credits',
        '  - Benefits & Tax credits page URL is correct')
      .setValue('input[name="child_benefit-per_interval_value"]', 0, function() {
        console.log('     • Child benefit is £0');
      })
      .setValue('input[name="child_tax_credit-per_interval_value"]', 0, function() {
        console.log('     • Investments is £0');
      })
      .click('input[name="other_benefits"][value="0"]', function() {
        console.log('     • Other benefits is ‘No’');
      })
      .conditionalFormSubmit(true, shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
