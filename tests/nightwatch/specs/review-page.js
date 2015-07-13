'use strict';

var _ = require('lodash');

var SCOPE_PATH = ['Debt', 'You own your own home', 'Yes'];

module.exports = {
  'Scope diagnosis': function(client) {
    client
      .startService()
      .scopeDiagnosis('In scope', SCOPE_PATH)
    ;
  },

  'Interstitial page': function(client) {
    client.interstitialPage();
  },

  'Means test': function(client) {
    client
      .aboutSetAllToYes(true)
      .selectBenefit('other-benefit', true)
      .fillInAdditionalBenefits(true)
      .fillInProperty(true)
      .fillInSavings(true)
      .fillInIncome(undefined, undefined, true)
      .fillInOutgoings(undefined, true)
    ;
  },

  'Review page': function(client) {
    client
      .assert.urlContains('/review', 'Review page URL is correct')
      .assert.elementPresent('#step-scope', 'Scope block is present')
      .assert.elementPresent('#step-about', 'About block is present')
      .assert.elementPresent('#step-benefits', 'Benefits block is present')
      .assert.elementPresent('#step-additional-benefits',
        'Additional benefits block is present')
      .assert.elementPresent('#step-property', 'Property block is present')
      .assert.elementPresent('#step-savings', 'Savings block is present')
      .assert.elementPresent('#step-income', 'Income block is present')
      .assert.elementPresent('#step-outgoings', 'Outgoings block is present')
      .execute(function(selector) {
        return $(selector).map(function() { return $(this).text() });
      }, ['#step-scope .answers-item .answer strong'],function(result) {
        this.assert.ok(_.difference(SCOPE_PATH, result.value).length === 0,
          'Answers in the scope block are the same as initially answered');
      })
      .end()
    ;
  }
};
