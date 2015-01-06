'use strict';

var _ = require('lodash');
var util = require('util');
var common = require('../modules/common-functions');
var CATEGORIES_OF_LAW = require('../modules/constants').CATEGORIES_OF_LAW;

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': function(client) {
    client
      .waitForElementVisible('form[action="/problem"]', 2000)
      .assert.urlContains('/problem')
      .assert.containsText('h1', 'What do you need help with?')
    ;
  },

  'Select nothing (error)': function(client) {
    common.submitAndCheckForError(client, 'Please select the area of law you need help with.');
  },

  'Check category outcomes': function(client) {
    CATEGORIES_OF_LAW.forEach(function(item) {
      var url = (item.covered ? '/about' : '/face-to-face');
      var el = (item.covered ? util.format('form[action="%s"]', url) : 'a[href="http://find-legal-advice.justice.gov.uk/"]');
      var headline = (item.covered ? 'About you' : util.format('We do not provide advice about issues related to %s', item.name.toLowerCase()));
      client
        .click(util.format('input[name="categories"][value="%s"]', item.value))
        .submitForm('form')
        .waitForElementVisible(el, 2000)
        .assert.urlContains(url,
          util.format('Goes to %s when ‘%s’ is selected', url, item.name)
        )
        .assert.containsText('h1', headline)
        .back()
        .waitForElementVisible('form[action="/problem"]', 2000)
      ;
    });

    client.end();
  }
};
