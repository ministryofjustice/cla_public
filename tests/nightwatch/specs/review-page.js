'use strict';

var _ = require('lodash');
var constants = require('../modules/constants');

module.exports = {
  '@disabled': true,
  'Scope diagnosis': function(client) {
    client
      .startService()
      .scopeDiagnosis(constants.SCOPE_PATHS.debtInScope)
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
      .fillInIncome(true, true, true)
      .fillInOutgoings(true, true)
    ;
  },

  'Review page': function(client) {
    client
      .ensureCorrectPage('.answers-summary', '/review', {
        '#step-scope h2': 'Your problem area',
        '#step-about h2': 'About you',
        '#step-benefits h2': 'You and your partner’s benefits',
        '#step-additional-benefits': 'You and your partner’s additional benefits',
        '#step-property': 'You and your partner’s property',
        '#step-savings': 'You and your partner’s savings',
        '#step-income': 'You and your partner’s income and tax',
        '#step-outgoings': 'You and your partner’s outgoings'
      })
      .execute(function(selector) {
        return $(selector).map(function() { return $(this).text() });
      }, ['#step-scope .answers-item .answer strong'],function(result) {
        this.assert.ok(_.difference(constants.SCOPE_PATHS.debtInScope, result.value).length === 0,
          'Answers in the scope block are the same as initially answered');
      })
      .end()
    ;
  }
};
