'use strict';

var log = require('../modules/log');

exports.command = function(eligibility, shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    var path = '/contact';

    if(eligibility === 'eligible') {
      path = '/result/eligible';
    }

    log.command('Processing Contact page…');

    client
      .assert.urlContains(path,
        '  - Contact page URL ' + path + ' is correct')
      .setValue('#full_name', 'John Smith')
      .click('input[name="callback_requested"][value="0"]')
      .conditionalFormSubmit(shouldSubmitForm)
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
