'use strict';

var util = require('util');
var common = require('../modules/common-functions');

var BENEFITS = [
  'income-support',
  'jobseekers-allowance',
  'guarantee-credit',
  'universal-credit',
  'employment-support',
  'other-benefit'
];

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    client
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'on_benefits', 1);
    client.submitForm('form');
  },

  'Benefits': function(client) {
    client
      .assert.urlContains('/benefits')
      .assert.containsText('h1', 'Your benefits')
    ;

    // test validation
    client.submitForm('form');
    common.submitAndCheckForError(client, 'Please select at least one option.');

    // test outcomes
    BENEFITS.forEach(function(item) {
      var destination = (item === 'other-benefit' ? '/benefits-tax-credits' : '/eligible');
      client
        .click(util.format('input[value="%s"]', item))
        .submitForm('form')
        .verify.urlContains(destination, util.format('Goes to %s when %s is checked', destination, item))
        .back()
        .click(util.format('input[value="%s"]', item))
    });

    client.end();
  }

};
