'use strict';

function testSidebar(client, headline) {
  client
    .assert.visible('aside.sidebar')
    .assert.containsText('aside.sidebar h2', headline)
  ;
}

module.exports = {
  'Progress indicator': function(client) {
    client
      .startService()
      .waitForElementVisible('.progress-bar', 1000, 'Progress sidebar exists')

      .assert.containsText('.progress-step.m-current', 'What do you need help with?',
        'Progress step is Problem page')
      .selectCategory('debt', true)

      .assert.containsText('.progress-step.m-current', 'About you',
        'Progress step is About page')
      .aboutSetAllToYes(true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s benefits',
        'Progress step is You and your partner’s benefits page')
      .selectBenefit('other-benefit', true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s property',
        'Progress step is You and your partner’s property')
      .fillInProperty(true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s savings',
        'Progress step is You and your partner’s savings')
      .fillInSavings(true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s benefits and tax credits',
        'Progress step is You and your partner’s benefits and tax credits')
      .fillInBenefitsAndTaxCredits(true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s income and tax',
        'Progress step is You and your partner’s income and tax')
      .fillInIncome(true, true)

      .assert.containsText('.progress-step.m-current', 'You and your partner’s outgoings',
        'Progress step is You and your partner’s outgoings')
      .fillInOutgoings(true)

      .assert.containsText('.progress-step.m-current', 'Review your answers',
        'Progress step is Review your answers')
      .conditionalFormSubmit(true)

      .assert.containsText('.progress-step.m-current', 'Contact information',
        'Progress step is Contact information')
      .fillInContactDetails(true)

      .assert.urlContains('/result/confirmation',
        'Confirmation page URL is correct')
    ;
    client.end();
  }
};
