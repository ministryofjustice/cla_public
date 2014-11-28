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
      .assert.attributeEquals('input[name="categories"][value="debt"]', 'checked', 'true')
      .submitForm('form')
    ;
  },

  aboutPageSetAllToNo: function(client) {
    this.setYesNoFields(client, ABOUT_YOU_QUESTIONS, 0);
  },

  setYesNoFields: function(client, fields, val) {
    var clickOption = function(client, field, val) {
      client.click(util.format('input[name="%s"][value="%s"]', field, val));
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
  submitAndCheckForFieldError: function(client, fieldName, errorText, tag) {
    tag = tag || "input";
    client
      .submitForm('form')
      .useXpath()
      .assert.containsText(util.format('//%s[@name="%s"]/ancestor::dl//div[@class="field-error"]', tag, fieldName), errorText)
      .useCss()
    ;
  },

  checkTextIsEqual: function(client, field, expectedText, xpath) {
    if(xpath) { // this may come in handy using CSS selectors later on
      client.useXpath();
    }
    client.getText(field, function(result) {
      this.assert.equal(result.value, expectedText, util.format('Text of <%s> exactly matches "%s"', field, expectedText));
    });
    if(xpath) {
      client.useCss();
    }
  },

  checkAttributeIsNotPresent: function(client, selector, attribute) {
    client
      .getAttribute(selector, attribute, function(result) {
        this.assert.equal(result.value, null, util.format('Checking selector %s does NOT have attribute %s: %s', selector, attribute, (result.value === null)));
      })
    ;
  }
};
