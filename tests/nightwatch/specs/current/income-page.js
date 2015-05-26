'use strict';

var util = require('util');
var common = require('../../modules/common-functions');
var EMPLOYMENT_QUESTIONS = require('../../modules/constants').EMPLOYMENT_QUESTIONS;
EMPLOYMENT_QUESTIONS.EMPLOYED = EMPLOYMENT_QUESTIONS.EMPLOYED_MANDATORY.concat(EMPLOYMENT_QUESTIONS.EMPLOYED_OPTIONAL);
EMPLOYMENT_QUESTIONS.ALL = EMPLOYMENT_QUESTIONS.EMPLOYED.concat(EMPLOYMENT_QUESTIONS.COMMON);
var other_income_amount = 'input[name="your_income-other_income-per_interval_value"]';

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes']);
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true);
  },

  'Income': function(client) {
    client
      .waitForElementVisible(other_income_amount, 5000)
      .assert.urlContains('/income')
      .assert.containsText('h1', 'Your money')
    ;
  },

  'Context-dependent questions for employment status': function(client) {
    client
      .back()
      .waitForElementVisible('input[name="have_partner"]', 5000)
      .setYesNoFields('is_employed', 1)
      .submitForm('form')
      .waitForElementVisible(other_income_amount, 5000)
    ;
    EMPLOYMENT_QUESTIONS.EMPLOYED.forEach(function(item) {
      client
        .assert.visible(util.format('[name="your_income-%s-per_interval_value"]', item))
        .assert.visible(util.format('[name="your_income-%s-interval_period"]', item))
      ;
    });

    client
      .back()
      .waitForElementVisible('input[name="have_partner"]', 5000)
      .setYesNoFields('is_employed', 0)
      .setYesNoFields('is_self_employed', 1)
      .submitForm('form')
      .waitForElementVisible(other_income_amount, 5000)
    ;
    EMPLOYMENT_QUESTIONS.EMPLOYED.forEach(function(item) {
      client
        .assert.visible(util.format('[name="your_income-%s-per_interval_value"]', item))
        .assert.visible(util.format('[name="your_income-%s-interval_period"]', item))
      ;
    });
  },

  'Context-dependent text and questions for partner': function(client) {
    client
      .assert.doesNotContainText('body', 'Your money')
      .assert.doesNotContainText('body', 'This section is for any money that is paid to you personally - for example, your wages. You should record income for your partner, if you have one, in the next section.')
    ;
    EMPLOYMENT_QUESTIONS.EMPLOYED.concat(EMPLOYMENT_QUESTIONS.COMMON).forEach(function(item) {
      client
        .assert.elementNotPresent(util.format('[name="partner_income-%s-per_interval_value"]', item))
        .assert.elementNotPresent(util.format('[name="partner_income-%s-interval_period"]', item))
      ;
    });

    client
      .back()
      .waitForElementVisible('input[name="have_partner"]', 5000)
      .setYesNoFields('have_partner', 1)
      .setYesNoFields(['in_dispute', 'is_self_employed', 'partner_is_self_employed'], 0)
      .setYesNoFields('partner_is_employed', 1)
      .submitForm('form')
      .waitForElementVisible(other_income_amount, 5000)
      .assert.containsText('h1', 'You and your partner’s money')
      .assert.containsText('body', 'Your money')
      .assert.containsText('body', 'Give details of any money that is paid to you personally, like your wages. Record money coming in for your partner in the next section.')
    ;
    EMPLOYMENT_QUESTIONS.COMMON.forEach(function(item) {
      client
        .assert.visible(util.format('[name="partner_income-%s-per_interval_value"]', item))
        .assert.visible(util.format('[name="partner_income-%s-interval_period"]', item))
      ;
    });
    client
      .back()
      .waitForElementVisible('input[name="have_partner"]', 5000)
      .setYesNoFields('is_employed', 1)
      .submitForm('form')
      .waitForElementVisible(other_income_amount, 5000)
    ;
    EMPLOYMENT_QUESTIONS.EMPLOYED.forEach(function(item) {
      client
        .assert.visible(util.format('[name="partner_income-%s-per_interval_value"]', item))
        .assert.visible(util.format('[name="partner_income-%s-interval_period"]', item))
      ;
    });
  },

  'Test validation': function(client) {
    var questions = [];
    ['your', 'partner'].forEach(function(person) {
      EMPLOYMENT_QUESTIONS.EMPLOYED_MANDATORY.forEach(function(item) {
        questions.push({
          name: util.format('%s_income-%s-per_interval_value', person, item),
          errorText: 'Please provide an amount'
        });
      });
    });
    common.submitAndCheckForFieldError(client, questions);

    ['your', 'partner'].forEach(function(person) {
      EMPLOYMENT_QUESTIONS.ALL.forEach(function(item) {
        client.setValue(util.format('[name=%s_income-%s-per_interval_value]', person, item), '250');
        common.submitAndCheckForFieldError(client, [{
          name: util.format('%s_income-%s-per_interval_value', person, item),
          errorText: 'Please select a time period from the drop down'
        }]);
        client
          .clearValue(util.format('[name=%s_income-%s-per_interval_value]', person, item))
          .setValue(util.format('[name=%s_income-%s-interval_period]', person, item), 'per month')
          .click('body')
        ;
        common.submitAndCheckForFieldError(client, [{
          name: util.format('%s_income-%s-interval_period', person, item),
          errorText: 'Please provide an amount'
        }], 'select');
      });
    });

    ['your', 'partner'].forEach(function(person) {
      EMPLOYMENT_QUESTIONS.ALL.forEach(function(item) {
        client
          .setValue(util.format('[name=%s_income-%s-per_interval_value]', person, item), '50')
          .setValue(util.format('[name=%s_income-%s-interval_period]', person, item), 'per month')
        ;
      });
    });
    client
      .click('body')
      .submitForm('form')
      .waitForElementVisible('input[name="income_contribution"]', 5000)
      .assert.urlContains('/outgoings')
    ;

    client.end();
  }

};
