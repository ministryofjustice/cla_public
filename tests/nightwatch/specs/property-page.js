'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var PROPERTY_QUESTIONS = require('../modules/constants').PROPERTY_QUESTIONS;

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    client
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'own_property', 1);
    client.submitForm('form');
  },

  'Property page': function(client) {
    client
      .assert.urlContains('/property')
      .assert.containsText('h1', 'Your property')
    ;
  },

  'Context-dependent text for partner': function(client) {
    client
      .assert.containsText('body', 'If you own more than one property, you can add more properties below.')
      .back();
    common.setYesNoFields(client, 'have_partner', 1);
    common.setYesNoFields(client, 'in_dispute', 0);
    common.setYesNoFields(client, ['partner_is_employed', 'partner_is_self_employed'], 0);
    client
      .submitForm('form')
      .assert.urlContains('/property')
      .assert.containsText('h1', 'You and your partner’s property')
      .assert.containsText('body', 'Please tell us about any property owned by you, your partner or both of you.')
      .assert.containsText('body', 'If you or your partner own more than one property, you can add more properties below.')
    ;
  },

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

    PROPERTY_QUESTIONS.forEach(function(item) {
      common.submitAndCheckForFieldError(client, item, 'Please choose Yes or No');
    });
    common.submitAndCheckForFieldError(client, 'properties-0-property_value', 'Please enter a valid amount');
    common.submitAndCheckForFieldError(client, 'properties-0-mortgage_remaining', 'Please select 0 if you have no mortgage');
    common.submitAndCheckForFieldError(client, 'properties-0-mortgage_payments', 'Number must be at least 0.');

    common.setYesNoFields(client, PROPERTY_QUESTIONS, 1);
    client
      .setValue('input[name="properties-0-property_value"]', '100000')
      .setValue('input[name="properties-0-mortgage_remaining"]', '90000')
      .setValue('input[name="properties-0-mortgage_payments"]', '1000')
      .setValue('#properties-0-rent_amount-per_interval_value', '')
      .setValue('#properties-0-rent_amount-interval_period', 'per month')
    ;
    common.submitAndCheckForFieldError(client, 'properties-0-is_rented', 'Not a valid amount');
    client
      .click(util.format('input[name="%s"][value="%s"]', 'properties-0-is_rented', 0))
      .submitForm('form')
      .assert.urlContains('/income')
    ;
  },

  'Add/remove properties': function(client) {
    client
      .back()
      .assert.elementPresent('fieldset#property-set-1')
      .assert.elementNotPresent('fieldset#property-set-2')
      .assert.elementNotPresent('fieldset#property-set-3')
      .click('[name="add-property"]')
      .waitForElementPresent('fieldset#property-set-2', 1000)
      .click('[name="add-property"]')
      .waitForElementPresent('fieldset#property-set-3', 1000)
      .assert.elementNotPresent('[name="add-property"]')
      .click('[name="remove-property-2"]')
      .assert.elementNotPresent('fieldset#property-set-3')
      .click('[name="remove-property-1"]')
      .assert.elementNotPresent('fieldset#property-set-2')
    ;

    client.end();
  }
};
