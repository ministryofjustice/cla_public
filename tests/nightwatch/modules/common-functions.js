'use strict';

var util = require('util');
var SAVINGS_QUESTIONS = require('../modules/constants').SAVINGS_QUESTIONS;
SAVINGS_QUESTIONS.ALL = SAVINGS_QUESTIONS.MONEY.concat(SAVINGS_QUESTIONS.VALUABLES);

module.exports = {
  setAllSavingsFieldsToValue: function(client, val) {
    SAVINGS_QUESTIONS.ALL.forEach(function(item) {
      client
        .clearValue(util.format('input[name="%s"]', item.name))
        .setValue(util.format('input[name="%s"]', item.name), val)
      ;
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
  submitAndCheckForFieldError: function(client, fields, tag) {
    tag = tag || "input";
    client
      .submitForm('form')
      .useXpath()
    ;
    fields.forEach(function(field) {
      client.assert.containsText(util.format('//%s[@name="%s"]/ancestor::fieldset', tag, field.name), field.errorText);
    });
    client.useCss();
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
  },

  // setValue on <select> items seems unreliable in nightwatch
  setDropdownValue: function(client, fieldName, value, verbose) {
    client
      .click(util.format('select[name="%s"]', fieldName))
      .click(util.format('select[name="%s"] option[value="%s"]', fieldName, value))
      .setValue(util.format('select[name="%s"]', fieldName), client.Keys.ENTER, function() {
        if(verbose && !!verbose) {
          console.log(util.format('Set %s to %s', fieldName, value));
        }
      })
    ;
  },

  humaniseValue: function(value) {
    var yesNo = {
      '1': 'Yes',
      '0': 'No'
    };

    return yesNo[value] || value;
  }
};
