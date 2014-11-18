'use strict';

var util = require('util');
var ABOUT_YOU_QUESTIONS = require('../modules/constants').ABOUT_YOU_QUESTIONS;

module.exports = {
  // skip start page
  startPage: function(client) {
    client
      .deleteCookies()
      .init()
      .maximizeWindow()
      .waitForElementVisible('body', 1000)
      .click('a.button-get-started')
    ;
  },

  // select a 'pass' category (debt) and move on to next page
  selectDebtCategory: function(client) {
    client
      .assert.urlContains('/problem')
      .assert.containsText('h1', 'What do you need help with?')
      .click('input[name="categories"][value="debt"]')
      .submitForm('form')
    ;
  },

  aboutPageSetAllToNo: function(client) {
    this.setYesNoFields(client, ABOUT_YOU_QUESTIONS, 0);
  },

  setYesNoFields: function(client, fields, val) {
    var clickOption = function(client, field, val) {
      client.click(util.format('input[name="%s"][value="%s"]', field, val), function() {
        console.log(util.format('Set %s to %s', field, (val === 1 ? 'yes' : 'no')));
      });
    };

    if(fields.constructor === Array) {
      fields.forEach(function(field) {
        clickOption(client, field, val);
      });
    } else {
      clickOption(client, fields, val);
    }
  },

  // Check validation
  // Expected to run on invalid form
  submitAndCheckForError: function(client, errorText) {
    client
      .submitForm('form')
      .assert.visible('.alert-error')
      .assert.containsText('.alert-error', errorText)
    ;
  },

  // check specific field group for error text
  submitAndCheckForFieldError: function(client, field, errorText) {
    client
      .submitForm('form')
      .useXpath()
      .assert.containsText(util.format('//input[@id="%s-0"]/ancestor::dl//*[@class="field-error"]', field), errorText)
      .useCss()
    ;
  },

  checkTextIsEqual: function(client, field, expectedText, xpath) {
    if(xpath) { // this may come in handy using CSS selectors later on
      client.useXpath();
    }
    client.getText(field, function(result) {
      this.assert.equal(result.value, expectedText, util.format('Text of %s exactly matches "%s"', field, expectedText));
    });
    if(xpath) {
      client.useCss();
    }
  }
};
