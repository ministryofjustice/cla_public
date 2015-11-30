'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var constants = require('../modules/constants');

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis(constants.SCOPE_PATHS.debtInScope);
  },

  'Interstitial page': function(client) {
    client.interstitialPage();
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true, {
      'on_benefits': 1
    });
  },

  'Benefits': function(client) {
    client.selectBenefit('other-benefit', true);
  },

  'Additional Benefits page': function(client) {
    client.ensureCorrectPage('#other_benefits-0', '/additional-benefits', {
      'h1': 'Your additional benefits'
    });
  },

  'Context-dependent text for partner': function(client) {
    client
      .back()
      .waitForElementVisible('#benefits-0', 5000,
        '  - Back to /benefits'
      )
      .back()
      .waitForElementVisible('#have_partner-0', 5000,
        '  - Back to /about'
      )
      .setYesNoFields('have_partner', 1)
      .pause(100)
      .setYesNoFields(['in_dispute', 'partner_is_employed', 'partner_is_self_employed'], 0)
      .conditionalFormSubmit(true)
      .waitForElementVisible('#benefits-0', 5000,
        '  - Back to /benefits'
      )
      .conditionalFormSubmit(true)
      .assert.containsText('h1', 'You and your partner’s additional benefits',
        '  - Page heading is correct (includes partner)'
      )
    ;
  },

  'Test validation': function(client) {
    client.ensureFormValidation();

    common.submitAndCheckForFieldError(client, [{
      name: 'other_benefits',
      errorText: 'Please choose Yes or No'
    }]);
    client.click('input[name="other_benefits"][value="1"]');
    common.submitAndCheckForFieldError(client, [{
      name: 'other_benefits',
      errorText: 'Please provide an amount'
    }]);
    client.setValue('input[name="total_other_benefit-per_interval_value"]', '100');
    common.submitAndCheckForFieldError(client, [{
      name: 'other_benefits',
      errorText: 'Please select a time period from the drop down'
    }]);
    client
      .clearValue('input[name="total_other_benefit-per_interval_value"]')
      .setValue('[name="total_other_benefit-interval_period"]', 'per month')
    ;
    common.submitAndCheckForFieldError(client, [{
      name: 'other_benefits',
      errorText: 'Please provide an amount'
    }]);
    client
      .setValue('input[name="total_other_benefit-per_interval_value"]', '100')
      .conditionalFormSubmit(true)
    ;
  }

};
