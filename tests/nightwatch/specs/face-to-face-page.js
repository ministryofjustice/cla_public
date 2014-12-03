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
      .assert.urlContains('/face-to-face')
      .assert.containsText('h1', 'You might qualify for legal aid, but we don\'t handle this type of problem')
      .click('article p:last-child a')
      .pause(1000)
      .assert.urlContains('find-legal-advice.justice.gov.uk')
    ;


    client.end();
  }

};
