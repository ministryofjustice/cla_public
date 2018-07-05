'use strict';

var constants = require('../modules/constants');

module.exports = {
  '@disabled': true,
  'Means test progress indicator': function(client) {
    client
      .startService()
      .scopeDiagnosis(constants.SCOPE_PATHS.debtInScope)
      .interstitialPage()
      .waitForElementVisible('.progress-bar', 1000,
        '  - Progress sidebar exists'
      )

      .assert.containsText('.progress-step.m-current', 'About you',
        '  - Progress step is About page')
      .aboutSetAllToYes(true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s benefits',
        '  - Progress step is You and your partner’s benefits page')
      .selectBenefit('other-benefit', true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s additional benefits',
        '  - Progress step is You and your partner’s additional benefits')
      .fillInAdditionalBenefits(true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s property',
        '  - Progress step is You and your partner’s property')
      .fillInProperty(true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s savings',
        '  - Progress step is You and your partner’s savings')
      .fillInSavings(true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s income and tax',
        '  - Progress step is You and your partner’s income and tax')
      .fillInIncome(true, true, true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s outgoings',
        '  - Progress step is You and your partner’s outgoings')
      .fillInOutgoings(true, true)

      .assert.containsText('.progress-step.m-current', 'Review your answers',
        '  - Progress step is Review your answers')
      .conditionalFormSubmit(true)

      .assert.containsText('.progress-step.m-current', 'Contact information',
        '  - Progress step is Contact information')
      .fillInContactDetails(true)

      .ensureCorrectPage('body.js-enabled', '/result/confirmation')
    ;
    client.end();
  }
};
