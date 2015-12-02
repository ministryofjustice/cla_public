'use strict';

var log = require('../modules/log');

exports.command = function(callback) {
  var client = this;

  this.perform(function() {
    log.command('Starting the service...');

    client
      .deleteCookies()
      .init()
      .maximizeWindow()
      .waitForElementVisible('body', 1000,
        '  - Page is ready')
      .assert.visible('aside.sidebar',
        '  - Page has sidebar')
      .click('a#start', function() {
        console.log('     ⟡ Start button clicked');
      })
      .pause(200)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
