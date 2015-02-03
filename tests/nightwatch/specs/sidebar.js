'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var SAVINGS_QUESTIONS = require('../modules/constants').SAVINGS_QUESTIONS;

function testSidebar(client, headline) {
  client
    .assert.visible('aside.sidebar')
    .assert.containsText('aside.sidebar h2', headline)
  ;
}

module.exports = {
  startPage: function(client) {
    client
      .deleteCookies()
      .init()
      .maximizeWindow()
      .waitForElementVisible('body', 1000)
    ;
    testSidebar(client, 'Resources');
    client.click('a#start');
  },

  'Categories of law (Your problem)': common.selectDebtCategory,

  'About you': function(client) {
    common.aboutPage(client);
    common.aboutPageSetAllToNo(client);
    common.setYesNoFields(client, 'is_employed', 1);
    common.setYesNoFields(client, 'have_savings', 1);
    client.submitForm('form');
  },

  'Savings page': function(client) {
    client
      .waitForElementVisible('input[name="savings"]', 2000)
      .assert.urlContains('/savings')
      .assert.containsText('h1', 'Your savings')
    ;
    testSidebar(client, 'Who can get legal aid?');
    SAVINGS_QUESTIONS.MONEY.forEach(function(item) {
      client.setValue(util.format('input[name="%s"]', item.name), 100);
    });
    client.submitForm('form');
  },

  'Income page': function(client) {
    client
      .waitForElementVisible('input[name="your_income-other_income-per_interval_value"]', 2000)
      .assert.urlContains('/income')
      .assert.containsText('h1', 'Your income')
    ;
    testSidebar(client, 'Who can get legal aid?');

    client.end();
  }
};
