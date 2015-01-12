'use strict';

var util = require('util');
var common = require('../modules/common-functions');

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    common.aboutPage(client);
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'on_benefits', 1);
    client.submitForm('form');
  },

  'Benefits': function(client) {
    client
      .waitForElementVisible('form[action="/benefits"]', 2000)
      .assert.urlContains('/benefits')
      .assert.containsText('h1', 'Your benefits')
      .assert.containsText('body', 'Are you on any of these benefits?')
      .click('input[value="income_support"]')
      .submitForm('form')
    ;
  },

  'Eligible page (request callback)': function(client) {
    client
      .waitForElementVisible('form[action="/call-me-back"]', 2000)
      .assert.urlContains('/result/eligible')
      .assert.containsText('h1', 'You might qualify for legal aid')
      .assert.containsText('h2', 'Request a callback')
      .assert.containsText('body', 'Based on the answers you’ve given today, you might qualify financially for legal aid.\nPlease submit your details below so we can call you back.')
    ;
  },

  'Validation': function(client) {
    client
      .submitForm('form')
    ;
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

    ['full_name', 'contact_number'].forEach(function(item) {
      common.submitAndCheckForFieldError(client, item, 'This field is required.');
    });
    client
      .setValue('input[name="full_name"]', 'John Doe')
      .setValue('input[name="contact_number"]', '12345')
    common.submitAndCheckForFieldError(client, 'safe_to_contact', 'Please choose Yes or No');
  },

  'Postcode address finder': function(client) {
    client
      // test for list of addresses for known postcode
      .setValue('input[name="post_code"]', 'e181ja')
      .click('.address-finder-button')
      .click('body')
      .waitForElementVisible('dd.address-list', 25000, false, function() {}, 'Element %s was not in the page for %d ms')
      .assert.value('input[name="post_code"]', 'E18 1JA')
      .assert.visible('dd.address-list')
      .assert.elementPresent('dd.address-list option[value="0"]')
      .assert.containsText('dd.address-list option[value="0"]', '3 Crescent Road, London, E18 1JA')
      .click('dd.address-list option[value="0"]')
      .click('body')
      .assert.value('#address', '3 Crescent Road\nLondon')

      // test for single address for known postcode
      .clearValue('input[name="post_code"]')
      .clearValue('#address')
      .setValue('input[name="post_code"]', 'sw1h9aj')
      .click('.address-finder-button')
      .click('body')
      .waitForElementNotPresent('dd.address-list', 25000, false, function() {}, 'Element %s was removed from the page after %d ms')
      .pause(1000)
      .assert.value('#address', 'Ministry of Justice\n102 Petty France\nLondon')

      // test for invalid postcode
      .clearValue('input[name="post_code"]')
      .clearValue('#address')
      .setValue('input[name="post_code"]', 'abcdefg')
      .click('.address-finder-button')
      .click('body')
      .useXpath()
      .waitForElementVisible('//input[@id="post_code"]/ancestor::fieldset//div[@class="field-error"]', 25000)
      .assert.containsText('//input[@id="post_code"]/ancestor::fieldset//div[@class="field-error"]', 'No addresses were found with that postcode')
      .useCss()
    ;

    client.end();
  }

};
