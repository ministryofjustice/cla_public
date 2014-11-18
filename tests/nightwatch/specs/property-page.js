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

  'Property': function(client) {
    // test context-dependent text for partner
    client
      .assert.urlContains('/property')
      .assert.containsText('h1', 'Your property')
    ;
    common.checkTextIsEqual(client, '//input[@id="properties-0-other_shareholders-0"]/ancestor::dl//*[@class="field-help"]', 'Other than you', true);
    client.back();
    common.setYesNoFields(client, 'have_partner', 1);
    client
      .submitForm('form')
      .assert.urlContains('/property')
      .assert.containsText('h1', 'You and your partner’s property')
    ;
    common.checkTextIsEqual(client, '//input[@id="properties-0-other_shareholders-0"]/ancestor::dl//*[@class="field-help"]', 'Other than you and your partner', true);


    // test validation
    common.submitAndCheckForError(client, 'This form has errors.\nPlease correct them and try again.');

    PROPERTY_QUESTIONS.forEach(function(item) {
      common.submitAndCheckForFieldError(client, item, 'Not a valid choice');
    });

    common.setYesNoFields(client, 'properties-0-is_rented', 1);
    client
      .setValue('#properties-0-rent_amount-amount', '')
      .setValue('#properties-0-rent_amount-interval', 'per month')
    ;
    common.submitAndCheckForFieldError(client, 'properties-0-is_rented', 'Not a valid amount');
    client
      .click(util.format('input[name="%s"][value="%s"]', 'properties-0-is_rented', 0))
      .submitForm('form')
      .verify.urlContains('/income')
    ;

    client.end();
  }

};
