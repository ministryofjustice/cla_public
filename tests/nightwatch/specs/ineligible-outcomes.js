'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var INELIGIBLE_OUTCOMES = require('../modules/constants').INELIGIBLE_OUTCOMES;

module.exports = {
  'Loop through eligible categories': function(client) {
    INELIGIBLE_OUTCOMES.forEach(function(item) {
      common.startPage(client);
      client
        .assert.urlContains('/problem')
        .click(util.format('input[name="categories"][value="%s"]', item.category.value))
        .submitForm('form')
        .assert.urlContains('/about')
      ;
      common.aboutPageSetAllToNo(client);
      common.setYesNoFields(client, 'have_savings', 1);
      client
        .submitForm('form')
        .assert.urlContains('/savings')
        .setValue('input[name="savings"]', '50000')
        .setValue('input[name="investments"]', '50000')
        .submitForm('form')
        .assert.urlContains('/help-organisations/' + item.category.label.toLowerCase().replace(/ /g, '-'))
        .assert.containsText('.org-list ul', item.link.text)

        // skipping this assertion for now as the data is iffy at present
        // .useXpath()
        // .assert.elementPresent(util.format('//div[@class="org-list"]/ul/li/a[@href="%s"]', encodeURI(item.link.href)))
        // .useCss()
      ;
    });

    client.end();
  }

};
