'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var OUTGOINGS_QUESTIONS = require('../modules/constants').OUTGOINGS_QUESTIONS;

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': function(client) {
    client
      .assert.urlContains('/problem')
      .assert.containsText('h1', 'What do you need help with?')
      .click('input[name="categories"][value="clinneg"]')
      .assert.attributeEquals('input[name="categories"][value="clinneg"]', 'checked', 'true')
      .submitForm('form')
    ;
  },

  'Face-to-face page': function(client) {
    client
      .waitForElementVisible('a[href="http://find-legal-advice.justice.gov.uk/"]', 2000)
      .assert.urlContains('/face-to-face')
      .assert.containsText('h1', 'We do not provide advice about issues related to clinical negligence')
    ;

    client.end();
  }

};
