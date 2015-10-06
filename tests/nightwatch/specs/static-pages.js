'use strict';

var util = require('util');

var STATIC_PAGES = [
  {
    url: "/cookies",
    headline: "Cookies"
  },
  {
    url: "/privacy",
    headline: "Terms and conditions and privacy"
  },
  {
    url: "/feedback",
    headline: "Your feedback"
  }
];

module.exports = {
  'Static pages': function(client) {
    client.startService();

    STATIC_PAGES.forEach(function(item) {
      client
        .useXpath()
        .click(util.format('//footer//a[@href="%s"]', item.url), function() {
          console.log(util.format('  • Clicked on `%s` link', item.url));
        })
        .useCss()
        .ensureCorrectPage('body.js-enabled', item.url, {
          'h1': item.headline
        })
      ;
    });
    client.end();
  }
};
