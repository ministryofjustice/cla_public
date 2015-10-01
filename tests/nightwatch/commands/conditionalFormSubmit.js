'use strict';

var url = require('url');

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    var urlBeforeSubmit;

    client.url(function(result) {
      urlBeforeSubmit = url.parse(result.value).pathname;
    });

    if(shouldSubmitForm) {
      client.submitForm('form', function() {
        console.log('     ⟡ Form submitted on', urlBeforeSubmit, 'page');

        this
          .waitForElementNotPresent('form > .alert-error', 500,
            '    - No form errors')
          .waitForElementPresent('body.js-enabled', 3000,
            '    - Next page is ready')
          .url(function(result) {
            this.assert.urlNotEqual(urlBeforeSubmit,
              '    - Next page: ' + url.parse(result.value).pathname);
          })
        ;
      });
    }
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
