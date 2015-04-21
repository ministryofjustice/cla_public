'use strict';

var log = require('../modules/log');

exports.command = function(categoryName, shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    log.command('Processing Problem page');

    client
      .assert.urlContains('/problem',
        '  - Problem page URL is correct')
      .assert.containsText('h1', 'What do you need help with?',
        '  - Problem page title is correct')
      .click('input[name="categories"][value="' + categoryName + '"]', function() {
        console.log('     • category ‘' + categoryName + '’ is selected');
      })
      .conditionalFormSubmit(shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
