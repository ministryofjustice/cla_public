'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var ABOUT_YOU_QUESTIONS = require('../modules/constants').ABOUT_YOU_QUESTIONS;

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
    common.startPage(client);
  },

  'Categories of law (Your problem)': function(client) {
    common.selectDebtCategory(client);
  },

  'About you': function(client) {
    client
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;

    // test validation
    common.submitAndCheckForError(client, 'This form has errors.\nPlease correct them and try again');
    ABOUT_YOU_QUESTIONS.forEach(function(item) {
      common.submitAndCheckForFieldError(client, item, 'Not a valid choice');
    });
    FIELDS_WITH_SUBFIELDS.forEach(function(item) {
      common.aboutYouSetAllToNo(client);
      client
        .verify.hidden(util.format('input[name="%s"]', item.subfield_name))
        .click(util.format('input[name="%s"][value="%s"]', item.field_name, 1))
        .verify.visible(util.format('input[name="%s"]', item.subfield_name))
        .submitForm('form')
      ;
      common.submitAndCheckForFieldError(client, item.field_name, item.errorText);
    });

    // test outcomes
    common.aboutYouSetAllToNo(client);
    client
      .submitForm('form')
      .verify.urlContains('/income', 'Goes to /income when all answers are No')
      .url(client.launch_url + '/about')
    ;
    OUTCOMES.forEach(function(item) {
      common.aboutYouSetAllToNo(client);
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
