'use strict';

var log = require('../modules/log');
var common = require('../modules/common-functions');

var ALL_INPUTS = {
  rent: { per_month: 0 },
  maintenance: { per_month: 0 },
  childcare: { per_month: 0 },
  income_contribution: 0
};

// Usage:
// ```
// client.fillInOutgoings({
//   rent: { per_week: 200 },
//   childcare: { per_month: 112 },
//   income_contribution: 0  // no period field
// });
// ```
//
// or `client.fillInOutgoings(true)` to use defaults (0s)

exports.command = function(inputs, shouldSubmitForm, callback) {
  var client = this;

  inputs = inputs === true ? ALL_INPUTS : inputs;
  inputs = common.formatMoneyInputs('', inputs);

  this.perform(function() {
    log.command('Processing Outgoings page…');

    client
      .waitForElementPresent('body.js-enabled', 3000, function() {
        console.log('     - Waiting for page to fully load');
      })
      .assert.urlContains('/outgoings', '  - Outgoings page URL is correct');
    common.fillInMoneyForm(client, inputs, 'Applicant');
    client.conditionalFormSubmit(shouldSubmitForm);
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
