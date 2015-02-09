'use strict';

var util = require('util');

var STATIC_PAGES = [
  {
    name: "cookies",
    headline: "Cookies"
  },
  {
    name: "privacy",
    headline: "Terms and conditions and privacy"
  },
  {
    name: "feedback",
    headline: "Your feedback"
  }
];

module.exports = {
  'Static pages': function(client) {
    client
      .deleteCookies()
      .init()
      .maximizeWindow()
      .waitForElementVisible('body', 1000)
    ;
    STATIC_PAGES.forEach(function(item) {
      client
        .useXpath()
        .click(util.format('//footer//a[@href="/%s"]', item.name))
        .useCss()
        .waitForElementVisible('body', 1000)
        .assert.containsText('h1', item.headline)
        .pause(1000)
      ;
    });
    client.end();
  }
};
