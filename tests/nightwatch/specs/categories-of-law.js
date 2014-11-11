'use strict';

var FAIL = {
  categories: [0, 1, 7, 8, 9, 10, 11],
  url: '/face-to-face',
  headline: 'We can’t help you with your problem'
};
var PASS = {
  categories: [2, 3, 4, 5, 6, 12, 13],
  url: '/about',
  headline: 'About you'
};

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
    ;
  },

  'Select failure categories': function(client) {
    FAIL.categories.forEach(function(item) {
      client
        .click('#categories-' + item)
        .submitForm('form')
        .verify.urlContains(FAIL.url)
        .verify.containsText('h1', FAIL.headline)
        .back()
      ;
    });
  },

  'Select success categories': function(client) {
    PASS.categories.forEach(function(item) {
      client
        .click('#categories-' + item)
        .submitForm('form')
        .verify.urlContains(PASS.url)
        .verify.containsText('h1', PASS.headline)
        .back()
      ;
    });

    client.end();
  }
};
