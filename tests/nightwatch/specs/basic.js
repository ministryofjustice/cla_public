'use strict';

// Check validation
// Expected to run on invalid form
function submitAndCheckForError(client, errorText) {
  client
    // .clearValue('input, textarea')
    .submitForm('form')
    .assert.visible('.alert-error')
    .assert.containsText('.alert-error', errorText)
  ;
}

module.exports = {
  'Start page': function(client) {
    client
      .deleteCookies()
      .init()
      .maximizeWindow()
      .waitForElementVisible('body', 1000)
      .assert.containsText('h1', 'Can I get legal aid?')
      .click('a.button-get-started')
    ;
  },

  'Categories of law (Your problem)': function(client) {
    client
      .assert.urlContains('/problem')
      .assert.containsText('h1', 'What do you need help with?')
    ;

    submitAndCheckForError(client, 'This field is required');

    client
      .click('#categories-0')
      .submitForm('form')
    ;
  },

  'About you': function(client) {
    client
      .assert.urlContains('/about')
      .assert.containsText('h1', 'About you')
    ;

    submitAndCheckForError(client, 'This form has errors');

    client
      .execute(function() {
        $('input[type=radio][value=1]').click();
      })
      .submitForm('form')
    ;
  },

  'Benefits': function(client) {
    client
      .assert.urlContains('/benefits')
      .assert.containsText('h1', 'Your benefits')
    ;

    submitAndCheckForError(client, 'Please select at least one option');

    client
      .click('input[value="other-benefit"]')
      .submitForm('form')
    ;
  },

  'Your property': function(client) {
    client
      .assert.urlContains('/property')
      .assert.containsText('h1', 'You and your partner’s property')
    ;

    submitAndCheckForError(client, 'This form has errors');

    client
      .execute(function() {
        $('input[type=radio][value=1]').click();
        $('input[type=text]').val(100);
      })
      .submitForm('form')
    ;
  },

  'You savings': function(client) {
    client
      .assert.urlContains('/savings')
      .assert.containsText('h1', 'You and your partner’s savings')
    ;

    submitAndCheckForError(client, 'This form has errors');

    client
      .execute(function() {
        $('input[type=text]').val(100);
      })
      .submitForm('form')
    ;
  },

  'Benefits and Tax Credits': function(client) {
    client
      .assert.urlContains('/benefits-tax-credits')
      .assert.containsText('h1', 'Your benefits and tax credits')
    ;

    submitAndCheckForError(client, 'This form has errors');

    client
      .execute(function() {
        $('input[type=radio][value=1]').click();
        $('input[type=text]').val(100);
      })
      .submitForm('form')
    ;
  },

  'Income': function(client) {
    client
      .assert.urlContains('/income')
      .assert.containsText('h1', 'Your income')
    ;

    submitAndCheckForError(client, 'This form has errors');

    client
      .execute(function() {
        $('input[type=text]').val(100);
      })
      .submitForm('form')
    ;
  },

  'Outgoings': function(client) {
    client
      .assert.urlContains('/outgoings')
      .assert.containsText('h1', 'Your outgoings')
    ;

    submitAndCheckForError(client, 'This form has errors');

    client
      .execute(function() {
        $('input[type=text]').val(100);
      })
      .submitForm('form')
    ;
  },

  'Result': function(client) {
    client
      .assert.urlContains('/result/')
      .assert.containsText('h1', 'You might qualify for legal aid with Civil Legal Advice')
      .end()
    ;
  }
};
