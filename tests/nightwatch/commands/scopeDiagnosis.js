'use strict';

var log = require('../modules/log');

exports.command = function(scenario, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Scope diagnosis - scenario: ' + scenario.title);

    client
      .waitForElementPresent('body.js-enabled', 3000, function() {
        console.log('     - Waiting for page to fully load');
      })
      .assert.urlContains('/scope/diagnosis',
        '  - Scope diagnosis URL is correct')
      .assert.containsText('h1', 'Choose the area you most need help with',
        '  - Scope diagnosis page title is correct')
      .useXpath()
    ;

    scenario.nodes.forEach(function(node) {
      var xpath = '//a[starts-with(normalize-space(.), "' + node + '")]';
      client
        .waitForElementPresent(xpath, 3000, '  • node ‘' + node + '’ visible')
        .pause(50) // KLUDGE: Wait a bit to ensure element is accessible before being clicked
        .click(xpath, function() {
          console.log('     • node ‘' + node + '’ clicked');
        });
    });

    client.useCss();
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
