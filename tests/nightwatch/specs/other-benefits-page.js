'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var constants = require('../modules/constants');

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  '@disabled': true,
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
    function checkForErrors(fields, errorText) {
      client.useXpath();
      fields.map(function (field) {
        client.assert.containsText(util.format('//*[@name="%s"]/ancestor::*[contains(@class, "form-group")]', field), errorText,
          util.format('    - `%s` has error message: `%s`', field, errorText));
      });
      client.useCss();
    }

    client.ensureFormValidation();

    checkForErrors(['other_benefits'], 'Please choose Yes or No');

    client
      .setYesNoFields('other_benefits', 1)
      .ensureFormValidation()
    ;

    checkForErrors(['total_other_benefit-per_interval_value'], 'Please provide an amount');

    client
      .setValue('input[name="total_other_benefit-per_interval_value"]', 100)
      .ensureFormValidation()
    ;

    checkForErrors(['total_other_benefit-interval_period'], 'Please select a time period from the drop down');

    client
      .selectDropdown('total_other_benefit-interval_period', 'per_week')
      .conditionalFormSubmit(true)
    ;
  }
};
