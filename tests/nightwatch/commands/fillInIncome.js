'use strict';

var log = require('../modules/log');
var common = require('../modules/common-functions');

var ALL_INPUTS = {
  earnings: { per_month: 0 },
  income_tax: { per_month: 0 },
  national_insurance: { per_month: 0 },
  working_tax_credit: { per_month: 0 },
  maintenance: { per_month: 0 },
  pension: { per_month: 0 },
  other_income: { per_month: 0 }
};

// Usage:
// ```
// client.fillInIncome({
//   earnings: { per_week: 620 },
//   other_income: { per_month: 400 }
// });
// ```
//
// or `client.fillInIncome(undefined)` to use defaults (0s)

exports.command = function(yourIncome, partnerIncome, shouldSubmitForm, callback) {
  var client = this;

  yourIncome = typeof yourIncome === 'undefined' ? ALL_INPUTS : yourIncome;
  partnerIncome = typeof partnerIncome === 'undefined' ? ALL_INPUTS : partnerIncome;

  var yourInputs = common.formatMoneyInputs('your_income-', yourIncome);
  var partnerInputs = common.formatMoneyInputs('partner_income-', partnerIncome);

  this.perform(function() {
    log.command('Processing Income page…');

    client.assert.urlContains('/income', '  - Income page URL is correct');

    common.fillInMoneyForm(client, yourInputs, 'Applicant');

    if(partnerIncome) {
      common.fillInMoneyForm(client, partnerInputs, 'Partner');
    }

    client.conditionalFormSubmit(shouldSubmitForm);
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
