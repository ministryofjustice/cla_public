'use strict';

var _ = require('lodash');
var util = require('util');

var CATEGORIES_OF_LAW = [
  'clinneg',
  'commcare',
  'debt',
  'discrimination',
  'education',
  'family',
  'housing',
  'immigration',
  'mentalhealth',
  'pi',
  'publiclaw',
  'aap',
  'violence',
  'benefits'
];

var NOT_COVERED = {
  categories: [
    'clinneg',
    'commcare',
    'immigration',
    'mentalhealth',
    'pi',
    'publiclaw',
    'aap'
  ],
  url: '/face-to-face',
  headline: 'We can’t help you with your problem'
};

var COVERED = {
  categories: _.difference(CATEGORIES_OF_LAW, NOT_COVERED.categories),
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
    NOT_COVERED.categories.forEach(function(item) {
      client
        .click(util.format('input[name="categories"][value="%s"]', item))
        .submitForm('form')
        .verify.urlContains(NOT_COVERED.url,
          util.format('Goes to %s when ‘%s’ is selected', NOT_COVERED.url, item)
        )
        .verify.containsText('h1', NOT_COVERED.headline)
        .back()
      ;
    });
  },

  'Select success categories': function(client) {
    COVERED.categories.forEach(function(item) {
      client
        .click(util.format('input[name="categories"][value="%s"]', item))
        .submitForm('form')
        .verify.urlContains(COVERED.url,
          util.format('Goes to %s when ‘%s’ is selected', COVERED.url, item)
        )
        .verify.containsText('h1', COVERED.headline)
        .back()
      ;
    });

    client.end();
  }
};
