'use strict';

var log = require('../modules/log');

exports.command = function(scenario, nodes, shouldContinue, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Scope diagnosis - scenario: ' + scenario);

    client
      .assert.urlContains('/scope/diagnosis',
        '  - Scope diagnosis URL is correct')
      .assert.containsText('h1', 'What do you need help with?',
        '  - Scope diagnosis page title is correct')
      .useXpath()
    ;

    nodes.forEach(function(node) {
      client.click('//a[starts-with(normalize-space(.), "' + node + '")]', function() {
        console.log('     • node ‘' + node + '’ is clicked');
      });
    });

    client.useCss();

    if(shouldContinue) {
      client.click('a.continue');
    }
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
