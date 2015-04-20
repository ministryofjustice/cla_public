'use strict';

var _ = require('lodash');
var util = require('util');
var common = require('../../modules/common-functions');
var CATEGORIES_OF_LAW = require('../../modules/constants').CATEGORIES_OF_LAW;

module.exports = {
  'Start page': common.startPage,

  'Categories of law (Your problem)': function(client) {
    client
      .waitForElementVisible('input[name="categories"]', 5000)
      .assert.urlContains('/problem')
      .assert.containsText('h1', 'What do you need help with?')
    ;
  },

  'Select nothing (error)': function(client) {
    common.submitAndCheckForError(client, 'Please select the area of law you need help with.');
  },

  'Check category outcomes': function(client) {
    CATEGORIES_OF_LAW.forEach(function(item) {
      var url = '/about';
      var el = 'input[name="have_partner"]';
      var headline = 'About you';
      if (!item.covered) {
        url = '/face-to-face';
        el = '.legal-adviser-search';
        headline = item.headline ||  'You may be able to get free advice from a legal adviser';
      }

      common.startPage(client);
      client
        .waitForElementVisible('input[name="categories"]', 5000)
        .assert.urlContains('/problem')
        .assert.containsText('h1', 'What do you need help with?')
        .click(util.format('input[name="categories"][value="%s"]', item.value))
        .submitForm('form')
        .waitForElementVisible(el, 5000)
        .assert.urlContains(url,
          util.format('Goes to %s when ‘%s’ is selected', url, item.name)
        )
        .assert.containsText('h1', headline)
      ;
    });

    client.end();
  }
};
