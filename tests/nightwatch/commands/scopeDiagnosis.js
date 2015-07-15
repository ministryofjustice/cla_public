'use strict';

var log = require('../modules/log');

exports.command = function(scenario, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Scope diagnosis - scenario: ' + scenario.title);

    client
      .assert.urlContains('/scope/diagnosis',
        '  - Scope diagnosis URL is correct')
      .assert.containsText('h1', 'What do you need help with?',
        '  - Scope diagnosis page title is correct')
      .useXpath()
    ;

    scenario.nodes.forEach(function(node) {
      var xpath = '//a[starts-with(normalize-space(.), "' + node + '")]';
      client
        .waitForElementVisible(xpath, 1000, '  • node ‘' + node + '’ visible')
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
