'use strict';

var log = require('../modules/log');
var common = require('../modules/common-functions');

var ALL_INPUTS = {
  earnings: { per_month: 0 },
  income_tax: { per_month: 0 },
  national_insurance: { per_month: 0 },
  child_tax_credit: { per_week: 0 },
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
// or `client.fillInIncome(true, true)` to use defaults (0s for applicant and partner)

exports.command = function(yourIncome, partnerIncome, shouldSubmitForm, callback) {
  var client = this;

  yourIncome = yourIncome === true ? ALL_INPUTS : yourIncome;
  partnerIncome = partnerIncome === true ? ALL_INPUTS : partnerIncome;

  var yourInputs = common.formatMoneyInputs('your_income-', yourIncome);
  var partnerInputs = common.formatMoneyInputs('partner_income-', partnerIncome);

  this.perform(function() {
    log.command('Processing Income page...');

    client.ensureCorrectPage('body.js-enabled', '/income');

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
