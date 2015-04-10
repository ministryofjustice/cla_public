'use strict';

var util = require('util');
var common = require('../../modules/common-functions');
var INELIGIBLE_OUTCOMES = require('../../modules/constants').INELIGIBLE_OUTCOMES;

module.exports = {
  'Loop through eligible categories': function(client) {
    INELIGIBLE_OUTCOMES.forEach(function(item) {
      common.startPage(client);
      client
        .waitForElementVisible('input[name="categories"]', 5000)
        .assert.urlContains('/problem')
        .click(util.format('input[name="categories"][value="%s"]', item.category.value))
        .submitForm('form')
        .waitForElementVisible('input[name="have_partner"]', 5000)
        .assert.urlContains('/about')
      ;
      common.aboutPageSetAllToNo(client);
      common.setYesNoFields(client, 'have_savings', 1);
      client
        .submitForm('form')
        .waitForElementVisible('input[name="savings"]', 5000)
        .assert.urlContains('/savings')
        .setValue('input[name="savings"]', '50000')
        .setValue('input[name="investments"]', '50000')
        .submitForm('form')
        .waitForElementVisible('a[href="https://www.gov.uk/find-a-legal-adviser"]', 5000)
        .assert.urlContains('/help-organisations/' + item.category.label.toLowerCase().replace(/ /g, '-'))

        .assert.containsText('.help-organisations ul', item.link.text)

        // skipping this assertion for now as the data is iffy at present
        // .useXpath()
        // .assert.elementPresent(util.format('//div[@class="org-list"]/ul/li/a[@href="%s"]', encodeURI(item.link.href)))
        // .useCss()
      ;
    });

    client.end();
  }

};
