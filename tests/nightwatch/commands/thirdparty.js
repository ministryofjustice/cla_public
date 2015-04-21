'use strict';

exports.command = function(isThirdparty, callback) {
  var client = this;

  this.perform(function() {
    if(isThirdparty) {
      client
        .click('input[name="third_party_handled"][value="1"]')
        .waitForElementVisible('#full_name', 5000,
          '  - Full name field is visible')
        .setValue('#full_name', 'John Smith')
        .waitForElementVisible('#third_party-third_party_name', 5000,
          '  - Third party name field is visible')
        .setValue('#third_party-third_party_name', 'James Bond')
        .waitForElementVisible('#third_party-relationship', 5000,
          '  - Third party relationship field is visible')
        .setValue('#third_party-relationship', 'OTHER')
      ;
    } else {
      client
        .click('input[name="third_party_handled"][value="0"]')
        .waitForElementVisible('#full_name', 5000,
          '  - Full name field is visible')
        .setValue('#full_name', 'John Smith')
      ;
    }
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
