'use strict';

var util = require('util');
var common = require('../../modules/common-functions');
var PROPERTY_QUESTIONS = require('../../modules/constants').PROPERTY_QUESTIONS;

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    common.aboutPage(client);
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'own_property', 1);
    client.submitForm('form');
  },

  'Property page': function(client) {
    client
      .waitForElementVisible('input[name="properties-0-is_main_home"]', 5000)
      .assert.urlContains('/property')
      .assert.containsText('h1', 'Your property')
    ;
  },

  'Context-dependent text for partner': function(client) {
    client
      .assert.containsText('body', 'If you own more than one property, you can add more properties below.')
      .back()
      .waitForElementVisible('input[name="have_partner"]', 5000)
    ;
    common.setYesNoFields(client, 'have_partner', 1);
    common.setYesNoFields(client, 'in_dispute', 0);
    common.setYesNoFields(client, ['partner_is_employed', 'partner_is_self_employed'], 0);
    client
      .submitForm('form')
      .waitForElementVisible('input[name="properties-0-is_main_home"]', 5000)
      .assert.urlContains('/property')
      .assert.containsText('h1', 'You and your partner’s property')
      .assert.containsText('body', 'Please tell us about any property owned by you, your partner or both of you.')
      .assert.containsText('body', 'If you or your partner own more than one property, you can add more properties below.')
    ;
  },

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

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
      errorText: 'Not a valid amount'
    });
    common.submitAndCheckForFieldError(client, questions);

    common.setYesNoFields(client, PROPERTY_QUESTIONS, 1);
    client
      .setValue('input[name="properties-0-property_value"]', '100000')
      .setValue('input[name="properties-0-mortgage_remaining"]', '90000')
      .setValue('input[name="properties-0-mortgage_payments"]', '1000')
      .setValue('#properties-0-rent_amount-per_interval_value', '')
      .setValue('#properties-0-rent_amount-interval_period', 'per month')
    ;

    client
      .click(util.format('input[name="%s"][value="%s"]', 'properties-0-is_rented', 0))
      .submitForm('form')
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000)
      .assert.urlContains('/income')
    ;
  },

  'Add/remove properties': function(client) {
    client
      .url(client.launch_url + '/property')
      .waitForElementVisible('input[name="properties-0-is_main_home"]', 5000)
      .assert.elementPresent('fieldset#property-set-1')
      .assert.elementNotPresent('fieldset#property-set-2')
      .assert.elementNotPresent('fieldset#property-set-3')
      .click('[name="add-property"]')
      .waitForElementPresent('fieldset#property-set-2', 5000)
      .click('[name="add-property"]')
      .waitForElementPresent('fieldset#property-set-3', 5000)
      .assert.elementNotPresent('[name="add-property"]')
      .click('[name="remove-property-2"]')
      .waitForElementNotPresent('fieldset#property-set-3', 25000, false, function() {}, 'Element %s was removed from the page after %d ms')
      .click('[name="remove-property-1"]')
      .waitForElementNotPresent('fieldset#property-set-2', 25000, false, function() {}, 'Element %s was removed from the page after %d ms')
    ;

    client.end();
  }
};
