'use strict';

var util = require('util');
var common = require('../../modules/common-functions');
var ABOUT_YOU_QUESTIONS = require('../../modules/constants').ABOUT_YOU_QUESTIONS;

var OUTCOMES = [
  {
    question: 'on_benefits',
    input: 'benefits',
    url: '/benefits'
  },
  {
    question: 'own_property',
    input: 'properties-0-is_main_home',
    url: '/property'
  },
  {
    question: 'have_savings',
    input: 'savings',
    url: '/savings'
  }
];
var FIELDS_WITH_SUBFIELDS = [
  {
    field_name: 'have_children',
    subfield_name: 'num_children',
    errorText: 'Number must be between 1 and 50'
  },
  {
    field_name: 'have_dependants',
    subfield_name: 'num_dependants',
    errorText: 'Number must be between 1 and 50'
  }
];

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': common.aboutPage,

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');
    ABOUT_YOU_QUESTIONS.forEach(function(item) {
      common.submitAndCheckForFieldError(client, item, 'Please choose Yes or No');
    });
    FIELDS_WITH_SUBFIELDS.forEach(function(item) {
      common.aboutPageSetAllToNo(client);
      client.assert.hidden(util.format('input[name="%s"]', item.subfield_name));
      common.setYesNoFields(client, item.field_name, 1);
      client.assert.visible(util.format('input[name="%s"]', item.subfield_name));
      common.setYesNoFields(client, item.field_name, 0);
      client.assert.hidden(util.format('input[name="%s"]', item.subfield_name));
      common.setYesNoFields(client, item.field_name, 1);
      common.submitAndCheckForFieldError(client, item.field_name, item.errorText);
    });
  },

  'Test outcomes': function(client) {
    common.aboutPageSetAllToNo(client);
    client
      .submitForm('form')
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000)
      .assert.urlContains('/income', 'Goes to /income when all answers are No')
      .url(client.launch_url + '/about')
      .waitForElementVisible('input[name="have_partner"]', 5000)
    ;
    OUTCOMES.forEach(function(item) {
      common.aboutPageSetAllToNo(client);
      common.setYesNoFields(client, item.question, 1);
      client
        .submitForm('form')
        .waitForElementVisible(util.format('input[name="%s"]', item.input), 5000)
        .assert.urlContains(item.url, util.format('Goes to %s when %s is Yes', item.url, item.question))
        .url(client.launch_url + '/about')
        .waitForElementVisible('input[name="have_partner"]', 5000)
      ;
    });

    client.end();
  }
};
