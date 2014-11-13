'use strict';

module.exports = {
  // Check validation
  // Expected to run on invalid form
  submitAndCheckForError: function(client, errorText) {
    client
      .submitForm('form')
      .assert.visible('.alert-error')
      .assert.containsText('.alert-error', errorText)
    ;
  }
};
