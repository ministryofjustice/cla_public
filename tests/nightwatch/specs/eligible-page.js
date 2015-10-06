'use strict';

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
    client
      .ensureCorrectPage('#benefits-0', '/benefits', {
        'h1': 'Your benefits',
        'fieldset legend': 'Which benefits do you receive?'
      })
      .click('input[value="income_support"]', function() {
        console.log('     • Select `income support`');
      })
      .conditionalFormSubmit(true)
    ;
  },

  'Review page': function(client) {
    client
      .waitForElementVisible('.answers-summary', 2000,
        '  - Page is ready')
      .conditionalFormSubmit(true)
    ;
  },

  'Eligible page (request callback)': function(client) {
    client.ensureCorrectPage('.contact-form', '/result/eligible', {
      'h1': 'Contact Civil Legal Advice'
    });
  },

  'Validation': function(client) {
    client
      .ensureFormValidation()
      .click('input[name="contact_type"][value="callback"]')
    ;

    ['full_name', 'callback-contact_number'].forEach(function(item) {
      common.submitAndCheckForFieldError(client, [{
        name: item,
        errorText: 'This field is required.'
      }]);
    });

    client.setValue('input[name="callback-contact_number"]', '12345');

    common.submitAndCheckForFieldError(client, [{
      name: 'callback-safe_to_contact',
      errorText: 'Please choose Yes or No'
    }]);
  },

  'Postcode address finder': function(client) {
    client
      // test for list of addresses for known postcode
      .setValue('input[name="address-post_code"]', 'e181ja', function() {
        console.log('     • Enter postcode `e181ja`');
      })
      .click('.address-finder-button', function() {
        console.log('     • Click on `Find UK address` button');
      })
      .click('body')
      .waitForElementVisible('div.address-list', 25000, false, function() {},
        '  - Element %s was not in the page for %d ms')
      .assert.value('input[name="address-post_code"]', 'E18 1JA',
        '  - Input value should become E18 1JA'
      )
      .assert.visible('div.address-list',
        '  - `.address-list` dropdown is visible'
      )
      .assert.elementPresent('div.address-list option[value="0"]',
        '  - `.address-list` dropdown has options'
      )
      .assert.containsText('div.address-list option[value="0"]', '3 Crescent Road, London, E18 1JA',
        '  - First option should be `3 Crescent Road, London, E18 1JA`'
      )
      .click('div.address-list option[value="0"]', function() {
        console.log('     • Click on the first option');
      })
      .click('body')
      .assert.valueContains('#address-street_address', '3 Crescent Road',
        '  - Address textarea should contain `3 Crescent Road`'
      )
      .assert.valueContains('#address-street_address', 'London',
        '  - Address textarea should also contain `London`'
      )

      // test for single address for known postcode
      .clearValue('input[name="address-post_code"]')
      .clearValue('#address-street_address', function() {
        console.log('     • Clear fields');
      })
      .setValue('input[name="address-post_code"]', 'sw1h9aj', function() {
        console.log('     • Enter postcode `sw1h9aj`');
      })
      .click('.address-finder-button', function() {
        console.log('     • Click on `Find UK address` button');
      })
      .click('body')
      .waitForElementNotPresent('div.address-list', 25000,
        '  - Element `%s` was removed from the page after %d ms')
      .pause(1000)
      .assert.valueContains('#address-street_address', 'Ministry of Justice',
        '  - Address textarea contains `Ministry of Justice`'
      )
      .assert.valueContains('#address-street_address', '102 Petty France',
        '  - Address textarea contains `102 Petty France`'
      )
      .assert.valueContains('#address-street_address', 'London',
        '  - Address textarea contains `London`'
      )

      // test for invalid postcode
      .clearValue('input[name="address-post_code"]')
      .clearValue('#address-street_address', function() {
        console.log('     • Clear fields');
      })
      .setValue('input[name="address-post_code"]', 'abcdefg', function() {
        console.log('     • Enter invalid postcode `abcdefg`');
      })
      .click('.address-finder-button', function() {
        console.log('     • Click on `Find UK address` button');
      })
      .click('body')
      .useXpath()
      .waitForElementVisible('//input[@id="address-post_code"]/ancestor::fieldset//div[@class="form-row field-error"]', 25000,
        '  - Field marked as invalid'
      )
      .assert.containsText('//input[@id="address-post_code"]/ancestor::fieldset//div[@class="form-row field-error"]', 'No addresses were found with that postcode, but you can still enter your address manually',
        ' - Field contains explanatory error text'
      )
      .useCss()
    ;

    client.end();
  }

};
