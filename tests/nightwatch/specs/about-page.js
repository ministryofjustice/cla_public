'use strict';

var util = require('util');
var common = require('../modules/common-functions');

var QUESTIONS = [
  'have_partner',
  'in_dispute',
  'on_benefits',
  'have_children',
  'have_dependants',
  'have_savings',
  'own_property',
  'is_employed',
  'is_self_employed',
  'aged_60_or_over'
];
var OUTCOMES = [
  {
    question: 'on_benefits',
    url: '/benefits'
  },
  {
    question: 'own_property',
    url: '/property'
  },
  {
    question: 'have_savings',
    url: '/savings'
  }
];
var FIELDS_WITH_SUBFIELDS = [
  {
    field_name: 'have_children',
    subfield_name: 'num_children',
    errorText: 'Please specify the number of children you have'
  },
  {
    field_name: 'have_dependants',
    subfield_name: 'num_dependants',
    errorText: 'Please specify the number of dependants you have'
  }
];

module.exports = {
  'Start page': function(client) {
    client
      .deleteCookies()
      .init()
      .maximizeWindow()
      .waitForElementVisible('body', 1000)
      .click('a.button-get-started')
    ;
  },

  'Categories of law (Your problem)': function(client) {
    client
      .assert.urlContains('/problem')
      .assert.containsText('h1', 'What do you need help with?')
      .click('input[name="categories"][value="debt"]')
      .submitForm('form')
    ;
  },

  'About you': function(client) {
    var allToNo = function(client) {
      QUESTIONS.forEach(function(item) {
        client.click(util.format('input[name="%s"][value="%s"]', item, 0));
      });
    };
    client
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;

    // test validation
    common.submitAndCheckForError(client, 'This form has errors.\nPlease correct them and try again');
    QUESTIONS.forEach(function(item) {
      common.submitAndCheckForFieldError(client, item, 'Not a valid choice');
    });
    FIELDS_WITH_SUBFIELDS.forEach(function(item) {
      allToNo(client);
      client
        .verify.hidden(util.format('input[name="%s"]', item.subfield_name))
        .click(util.format('input[name="%s"][value="%s"]', item.field_name, 1))
        .verify.visible(util.format('input[name="%s"]', item.subfield_name))
        .submitForm('form')
      ;
      common.submitAndCheckForFieldError(client, item.field_name, item.errorText);
    });

    // test outcomes
    allToNo(client);
    client
      .submitForm('form')
      .verify.urlContains('/income', 'Goes to /income when all answers are No')
      .url(client.launch_url + '/about')
    ;
    OUTCOMES.forEach(function(item) {
      allToNo(client);
      client
        .click(util.format('input[name="%s"][value="%s"]', item.question, 1))
        .submitForm('form')
        .verify.urlContains(item.url, util.format('Goes to %s when %s is Yes', item.url, item.question))
        .back()
      ;
    });

    client.end();
  }
};
