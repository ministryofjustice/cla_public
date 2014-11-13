'use strict';

var _ = require('lodash');
var util = require('util');

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

    allToNo(client);
    client
      .submitForm('form')
      .verify.urlContains('/income', 'Goes to /income when all answers are No')
      .back()
    ;

    OUTCOMES.forEach(function(item) {
      allToNo(client);
      client
        .click(util.format('input[name="%s"][value="%s"]', item.question, 1))
        .submitForm('form')
        .verify.urlContains(item.url, util.format('Goes to %s when %s is Yes', item.url, item.question))
        .back()
    });

    client.end();
  }
};
