'use strict';

var common = require('../../modules/common-functions');

module.exports = {
  'Start page': common.startPage,

  'Scope diagnosis': function(client) {
    client
      .assert.urlContains('/scope/diagnosis')
      .assert.containsText('h1', 'What do you need help with?')
      .useXpath()
      .click('//a[@href="/scope/diagnosis/n65::n0"]')
      .useCss()
    ;
  },

  'Face-to-face page': function(client) {
    client
      .waitForElementVisible('.legal-adviser-search', 5000)
      .assert.urlContains('/face-to-face')
      .assert.containsText('h1', 'You may be able to get advice from a legal adviser')
      .checkFlashMessage()
    ;
  },

  'Find legal adviser search': function(client) {
    client
      .setValue('input[name="postcode"]', 'w22dd')
      .submitForm('form')
      .assert.urlContains('/face-to-face')
      .waitForElementVisible('.search-results-container', 5000)
      .assert.containsText('.results-location', 'W2 2DD')
    ;

    client.end();
  }

};
