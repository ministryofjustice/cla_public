'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var constants = require('../modules/constants');
var ABOUT_YOU_QUESTIONS = constants.ABOUT_YOU_QUESTIONS;

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
    client.scopeDiagnosis(constants.SCOPE_PATHS.debtInScope);
  },

  'Interstitial page': function(client) {
    client.interstitialPage();
  },

  'Test validation': function(client) {
    client.ensureFormValidation();

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
        .assert.hidden(util.format('input[name="%s"]', item.subfield_name),
          util.format('    - `%s` field is hidden', item.subfield_name)
        )
        .setYesNoFields(item.field_name, 1)
        .pause(100)
        .assert.visible(util.format('input[name="%s"]', item.subfield_name),
          util.format('    - `%s` field is visible', item.subfield_name)
        )
        .setYesNoFields(item.field_name, 0)
        .pause(100)
        .assert.hidden(util.format('input[name="%s"]', item.subfield_name),
          util.format('    - `%s` field is hidden again', item.subfield_name)
        )
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
      .url(client.launch_url + '/about')
      .waitForElementVisible('#have_partner-0', 5000,
        '  ⟡ Go back to /about'
      )
    ;
    OUTCOMES.forEach(function(item) {
      var selection = {};
      selection[item.question] = 1;
      client
        .aboutSetAllToNo(true, selection)
        .url(client.launch_url + '/about')
        .waitForElementVisible('#have_partner-0', 5000,
          '  ⟡ Go back to /about'
        )
      ;
    });

    client.end();
  }
};
