'use strict';

var common = require('../modules/common-functions');

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes']);
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
    client
      .waitForElementVisible('input[name="benefits"]', 5000)
      .assert.urlContains('/benefits')
      .assert.containsText('h1', 'Your benefits')
      .assert.containsText('body', 'Which benefits do you receive?')
      .click('input[value="income_support"]')
      .submitForm('form')
    ;
  },

  'Review page': function(client) {
    client
      .waitForElementVisible('.answers-summary', 2000)
      .submitForm('form')
    ;
  },

  'Eligible page (request callback)': function(client) {
    client
      .assert.urlContains('/result/eligible')
      .waitForElementVisible('input[name="contact_type"]', 5000)
      .assert.containsText('h1', 'Contact Civil Legal Advice')
      .assert.containsText('body', 'Based on the answers you’ve given today, you might qualify for legal aid.')
    ;
  },

  'Validation': function(client) {
    client
      .submitForm('form')
    ;
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');

    client
      .click('input[name="contact_type"][value="callback"]')
    ;

    ['full_name', 'callback-contact_number'].forEach(function(item) {
      common.submitAndCheckForFieldError(client, [{
        name: item,
        errorText: 'This field is required.'
      }]);
    });
    client
      .setValue('input[name="callback-contact_number"]', '12345');
    common.submitAndCheckForFieldError(client, [{
      name: 'callback-safe_to_contact',
      errorText: 'Please choose Yes or No'
    }]);
  },

  'Postcode address finder': function(client) {
    client
      // test for list of addresses for known postcode
      .setValue('input[name="address-post_code"]', 'e181ja')
      .click('.address-finder-button')
      .click('body')
      .waitForElementVisible('div.address-list', 25000, false, function() {}, 'Element %s was not in the page for %d ms')
      .assert.value('input[name="address-post_code"]', 'E18 1JA')
      .assert.visible('div.address-list')
      .assert.elementPresent('div.address-list option[value="0"]')
      .assert.containsText('div.address-list option[value="0"]', '3 Crescent Road, London, E18 1JA')
      .click('div.address-list option[value="0"]')
      .click('body')
      .assert.valueContains('#address-street_address', '3 Crescent Road')
      .assert.valueContains('#address-street_address', 'London')

      // test for single address for known postcode
      .clearValue('input[name="address-post_code"]')
      .clearValue('#address-street_address')
      .setValue('input[name="address-post_code"]', 'sw1h9aj')
      .click('.address-finder-button')
      .click('body')
      .waitForElementNotPresent('div.address-list', 25000, false, function() {}, 'Element %s was removed from the page after %d ms')
      .pause(1000)
      .assert.valueContains('#address-street_address', 'Ministry of Justice')
      .assert.valueContains('#address-street_address', '102 Petty France')
      .assert.valueContains('#address-street_address', 'London')

      // test for invalid postcode
      .clearValue('input[name="address-post_code"]')
      .clearValue('#address-street_address')
      .setValue('input[name="address-post_code"]', 'abcdefg')
      .click('.address-finder-button')
      .click('body')
      .useXpath()
      .waitForElementVisible('//input[@id="address-post_code"]/ancestor::fieldset//div[@class="form-row field-error"]', 25000)
      .assert.containsText('//input[@id="address-post_code"]/ancestor::fieldset//div[@class="form-row field-error"]', 'No addresses were found with that postcode, but you can still enter your address manually')
      .useCss()
    ;

    client.end();
  }

};
