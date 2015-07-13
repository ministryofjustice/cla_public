'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var ABOUT_YOU_QUESTIONS = require('../modules/constants').ABOUT_YOU_QUESTIONS;

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
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes']);
  },

  'Interstitial page': function(client) {
    client.interstitialPage();
  },

  'Test validation': function(client) {
    common.submitAndCheckForError(client, 'This form has errors.\nPlease see below for the errors you need to correct.');
    var questions = [];
    ABOUT_YOU_QUESTIONS.forEach(function(item) {
      questions.push({
        name: item,
        errorText: 'Please choose Yes or No'
      });
    });
    common.submitAndCheckForFieldError(client, questions);

    FIELDS_WITH_SUBFIELDS.forEach(function(item) {
      client
        .aboutSetAllToNo(false)
        .assert.hidden(util.format('input[name="%s"]', item.subfield_name))
        .setYesNoFields(item.field_name, 1)
        .assert.visible(util.format('input[name="%s"]', item.subfield_name))
        .setYesNoFields(item.field_name, 0)
        .assert.hidden(util.format('input[name="%s"]', item.subfield_name))
        .setYesNoFields(item.field_name, 1)
      ;
      common.submitAndCheckForFieldError(client, [{
        name: item.field_name,
        errorText: item.errorText
      }]);
    });
  },

  'Test outcomes': function(client) {
    client
      .aboutSetAllToNo(true)
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 5000)
      .assert.urlContains('/income', 'Goes to /income when all answers are No')
      .url(client.launch_url + '/about')
      .waitForElementVisible('input[name="have_partner"]', 5000)
    ;
    OUTCOMES.forEach(function(item) {
      var selection = {};
      selection[item.question] = 1;
      client
        .aboutSetAllToNo(true, selection)
        .waitForElementVisible(util.format('input[name="%s"]', item.input), 5000)
        .assert.urlContains(item.url, util.format('Goes to %s when %s is Yes', item.url, item.question))
        .url(client.launch_url + '/about')
        .waitForElementVisible('input[name="have_partner"]', 5000)
      ;
    });

    client.end();
  }
};
