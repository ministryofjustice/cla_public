var config = require('../config.json');

module.exports = {
  "Click through pages" : function (browser) {
    browser
      .url(config.url)
      .waitForElementVisible('body', 1000)
      .assert.containsText('h1', 'Can I get legal aid?')
      .click('a.button-get-started')

      .assert.urlContains('/problem')
      .assert.containsText('h1', 'What do you need help with?')
      .submitForm('form')

      .assert.visible('.alert-error')
      .assert.containsText('.alert-error', 'Not a valid choice')

      .click('#categories-0')
      .submitForm('form')

      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
      .click('#proceed')
      .submitForm('form')

      .assert.urlContains('/benefits')
      .assert.containsText('h1', 'Your benefits')
      .click('#proceed')
      .submitForm('form')

      .assert.urlContains('/property')
      .assert.containsText('h1', 'Your property')
      .click('#proceed')
      .submitForm('form')

      .assert.urlContains('/savings')
      .assert.containsText('h1', 'Your savings')
      .click('#proceed')
      .submitForm('form')

      .assert.urlContains('/benefits-tax-credits')
      .assert.containsText('h1', 'Your benefits and tax credits')
      .click('#proceed')
      .submitForm('form')

      .assert.urlContains('/income')
      .assert.containsText('h1', 'Your income')
      .click('#proceed')
      .submitForm('form')

      .assert.urlContains('/outgoings')
      .assert.containsText('h1', 'Your outgoings')

      .click('#result-0')
      .submitForm('form')
      .assert.urlContains('/eligible')
      .assert.containsText('h1', 'You might qualify for legal aid with Civil Legal Advice')

      .back()
      .click('#result-1')
      .submitForm('form')
      .assert.urlContains('/ineligible')
      .assert.containsText('h1', 'You’re unlikely to get legal aid')

      .back()
      .click('#result-2')
      .submitForm('form')
      .assert.urlContains('/face-to-face')
      .assert.containsText('h1', 'We can’t help you with your problem')

      .back()
      .click('#result-3')
      .submitForm('form')
      .assert.urlContains('/confirmation')
      .assert.containsText('h1', 'We will call you back')


      .end();
  }
};
