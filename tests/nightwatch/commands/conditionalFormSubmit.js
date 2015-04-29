'use strict';

exports.command = function(shouldSubmitForm, callback) {
  var client = this;

  this.perform(function() {
    if(shouldSubmitForm) {
      client.submitForm('form', function() {
        console.log('     ◇ Form submitted');
      });
    }
  });

  return client;
};
