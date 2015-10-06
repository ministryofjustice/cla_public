'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var constants = require('../modules/constants');

var PROPERTY_QUESTIONS = constants.PROPERTY_QUESTIONS;

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
      'own_property': 1
    });
  },

  'Property page': function(client) {
    client.ensureCorrectPage('#properties-0-is_main_home-0', '/property', {
      'h1': 'Your property'
    });
  },

  'Context-dependent text for partner': function(client) {
    client
      .back()
      .ensureCorrectPage('#have_partner-0', '/about')
      .setYesNoFields('have_partner', 1)
      .pause(100)
      .setYesNoFields(['in_dispute', 'partner_is_employed', 'partner_is_self_employed'], 0)
      .conditionalFormSubmit(true)
      .ensureCorrectPage('#properties-0-is_main_home-0', '/property', {
        'h1': 'You and your partner’s property',
        'body': 'Please tell us about any property owned by you, your partner or both of you'
      })
    ;
  },

  'Test validation': function(client) {
    client.ensureFormValidation();

    var questions = [];
    PROPERTY_QUESTIONS.forEach(function(item) {
      questions.push({
        name: item,
        errorText: 'Please choose Yes or No'
      });
    });
    questions.push({
      name: 'properties-0-property_value',
      errorText: 'Please enter a valid amount'
    });
    questions.push({
      name: 'properties-0-mortgage_remaining',
      errorText: 'Please enter 0 if you have no mortgage'
    });
    questions.push({
      name: 'properties-0-mortgage_payments',
      errorText: 'Please enter 0 if you have no mortgage'
    });
    common.submitAndCheckForFieldError(client, questions);

    client
      .setYesNoFields(PROPERTY_QUESTIONS, 1)
      .setValue('input[name="properties-0-property_value"]', '100000')
      .setValue('input[name="properties-0-mortgage_remaining"]', '90000')
      .setValue('input[name="properties-0-mortgage_payments"]', '1000')
      .setValue('#properties-0-rent_amount-per_interval_value', '')
      .setValue('#properties-0-rent_amount-interval_period', 'per month')
    ;

    client
      .click(util.format('input[name="%s"][value="%s"]', 'properties-0-is_rented', 0))
      .conditionalFormSubmit(true)
    ;
  },

  'Add/remove properties': function(client) {
    client
      .url(client.launch_url + '/property')
      .ensureCorrectPage('#properties-0-is_main_home-0', '/property')
      .assert.elementPresent('fieldset#property-set-1',
        '  - Property fieldset 1 is present'
      )
      .assert.elementNotPresent('fieldset#property-set-2',
        '  - Property fieldset 2 is absent'
      )
      .assert.elementNotPresent('fieldset#property-set-3',
        '  - Property fieldset 3 is absent'
      )
      .click('[name="add-property"]', function() {
        console.log('     • Click "Add property"');
      })
      .waitForElementPresent('fieldset#property-set-2', 5000,
        '  - Property fieldset 2 is present'
      )
      .click('[name="add-property"]', function() {
        console.log('     • Click "Add property"');
      })
      .waitForElementPresent('fieldset#property-set-3', 5000,
        '  - Property fieldset 3 is present'
      )
      .assert.elementNotPresent('[name="add-property"]',
        '  - "Add property" button is absent'
      )
      .click('[name="remove-property-2"]', function() {
        console.log('     • Click "remove property 2"');
      })
      .waitForElementNotPresent('fieldset#property-set-3', 25000,
        '  - Property fieldset 3 is absent'
      )
      .click('[name="remove-property-1"]', function() {
        console.log('     • Click "remove property 2"');
      })
      .waitForElementNotPresent('fieldset#property-set-2', 25000,
        '  - Property fieldset 2 is absent'
      )
    ;

    client.end();
  }
};
