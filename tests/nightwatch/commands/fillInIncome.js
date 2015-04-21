'use strict';

var log = require('../modules/log');

exports.command = function(hasPartner, shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Income page…');

    client
      .assert.urlContains('/income',
        '  - Income page URL is correct')
      .setValue('input[name="your_income-earnings-per_interval_value"]', 0, function() {
        console.log('     • Applicant: Wages before tax is £0');
      })
      .setValue('input[name="your_income-income_tax-per_interval_value"]', 0, function() {
        console.log('     • Applicant: Income tax is £0');
      })
      .setValue('input[name="your_income-national_insurance-per_interval_value"]', 0, function() {
        console.log('     • Applicant: NI contributions is £0');
      })
      .setValue('input[name="your_income-working_tax_credit-per_interval_value"]', 0, function() {
        console.log('     • Applicant: Working tax credit is £0');
      })
      .setValue('input[name="your_income-maintenance-per_interval_value"]', 0, function() {
        console.log('     • Applicant: Maintenance received is £0');
      })
      .setValue('input[name="your_income-pension-per_interval_value"]', 0, function() {
        console.log('     • Applicant: Pension received is £0');
      })
      .setValue('input[name="your_income-other_income-per_interval_value"]', 0, function() {
        console.log('     • Applicant: Other income is £0');
      })
    ;

    if(hasPartner) {
      client
        .setValue('input[name="partner_income-earnings-per_interval_value"]', 0, function() {
          console.log('     • Partner: Wages before tax is £0');
        })
        .setValue('input[name="partner_income-income_tax-per_interval_value"]', 0, function() {
          console.log('     • Partner: Income tax is £0');
        })
        .setValue('input[name="partner_income-national_insurance-per_interval_value"]', 0, function() {
          console.log('     • Partner: NI contributions is £0');
        })
        .setValue('input[name="partner_income-working_tax_credit-per_interval_value"]', 0, function() {
          console.log('     • Partner: Working tax credit is £0');
        })
        .setValue('input[name="partner_income-maintenance-per_interval_value"]', 0, function() {
          console.log('     • Partner: Maintenance received is £0');
        })
        .setValue('input[name="partner_income-pension-per_interval_value"]', 0, function() {
          console.log('     • Partner: Pension received is £0');
        })
        .setValue('input[name="partner_income-other_income-per_interval_value"]', 0, function() {
          console.log('     • Partner: Other income is £0');
        })
      ;
    }

    if(shouldSubmitForm) {
      client.conditionalFormSubmit(shouldSubmitForm);
    }
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
