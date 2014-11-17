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

  aboutYouSetAllToNo: function(client) {
    ABOUT_YOU_QUESTIONS.forEach(function(item) {
      client.click(util.format('input[name="%s"][value="%s"]', item, 0));
    });
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
  }
};
