'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var constants = require('../modules/constants');
var BENEFITS = constants.BENEFITS;

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
    client.ensureCorrectPage('#benefits-0', '/benefits', {
      'h1': 'Your benefits',
      'fieldset legend': 'Which benefits do you receive?'
    });
  },

  'Context-dependent text and headline for partner': function(client) {
    client
      .assert.doesNotContainText('h1', 'You and your partner’s benefits',
        '  - Title is correct'
      )
      .assert.doesNotContainText('fieldset legend', 'Which benefits do you and your partner receive?',
        '  - Doesn’t mention partner'
      )
      .back()
      .waitForElementVisible('#have_partner-0', 5000,
        '  - Page is ready'
      )
      .setYesNoFields('have_partner', 1)
      .pause(100)
      .setYesNoFields(['in_dispute', 'partner_is_employed', 'partner_is_self_employed'], 0)
      .submitForm('form', function() {
        console.log('     ⟡ Form submitted');
      })
      .waitForElementVisible('#benefits-0', 5000,
        '    - On /benefits page'
      )
      .assert.containsText('h1', 'You and your partner’s benefits',
        '    - Title is correct'
      )
      .assert.containsText('body', 'Which benefits do you and your partner receive?',
        '    - Field legend text is correct (with partner)'
      )
    ;
  },

  'Test validation': function(client) {
    client.ensureFormValidation();
  },

  'Test outcomes': function(client) {
    BENEFITS.forEach(function(item) {
      var destination = (item === 'other-benefit' ? '/additional-benefits' : '/review');
      var waitElement = (item === 'other-benefit' ? '#other-benefits-0' : '.answers-summary');
      client
        .click(util.format('input[value="%s"]', item))
        .conditionalFormSubmit(true)
        .assert.urlContains(destination,
          util.format('    - Goes to %s when `%s` is checked', destination, item)
        )
        .url(client.launch_url + '/benefits')
        .waitForElementVisible('#benefits-0', 5000,
          '    - Back to /benefits page'
        )
        .click(util.format('input[value="%s"]', item))
      ;
    });

    client.end();
  }

};
