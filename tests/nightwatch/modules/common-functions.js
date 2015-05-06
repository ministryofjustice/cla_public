'use strict';

var util = require('util');
var ABOUT_YOU_QUESTIONS = require('../modules/constants').ABOUT_YOU_QUESTIONS;
var SAVINGS_QUESTIONS = require('../modules/constants').SAVINGS_QUESTIONS;
SAVINGS_QUESTIONS.ALL = SAVINGS_QUESTIONS.MONEY.concat(SAVINGS_QUESTIONS.VALUABLES);

module.exports = {
  // skip start page
  startPage: function(client, msg) {
    client
      .deleteCookies()
      .init()
      .maximizeWindow()
      .waitForElementVisible('body', 5000)
      .click('a#start', function() {
        if(msg) {
          console.log('\n' + msg + '\n');
        }
      })
    ;
  },

  // select a 'pass' category (debt) and move on to next page
  selectDebtCategory: function(client) {
    client
      .waitForElementVisible('input[name="categories"]', 5000)
      .assert.urlContains('/problem')
      .assert.containsText('h1', 'What do you need help with?')
      .click('input[name="categories"][value="debt"]')
      .assert.attributeEquals('input[name="categories"][value="debt"]', 'checked', 'true')
      .submitForm('form')
    ;
  },

  aboutPage: function(client) {
    client
      .waitForElementVisible('input[name="have_partner"]', 5000)
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;
  },

  aboutPageSetAllToNo: function(client) {
    this.setYesNoFields(client, ABOUT_YOU_QUESTIONS, 0);
  },

  setYesNoFields: function(client, fields, val) {
    var clickOption = function(client, field, val) {
      var el = util.format('input[name="%s"][value="%s"]', field, val);
      client.isVisible(el, function(result) {
        if(result.value === true) {
          client.click(el);
        }
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
