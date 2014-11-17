'use strict';

var util = require('util');

module.exports = {
  // Check validation
  // Expected to run on invalid form
  submitAndCheckForError: function(client, errorText) {
    client
      .submitForm('form')
      .assert.visible('.alert-error')
      .assert.containsText('.alert-error', errorText)
    ;
  },

  submitAndCheckForFieldError: function(client, field, errorText) {
    client
      .submitForm('form')
      .useXpath()
      .assert.containsText(util.format('//input[@id="%s-0"]/ancestor::dl//*[@class="field-error"]', field), errorText)
      .useCss()
    ;
  }
};
