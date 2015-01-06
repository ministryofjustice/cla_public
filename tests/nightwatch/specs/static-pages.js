'use strict';

module.exports = {
  'Cookies page': function(client) {
    client
      .init(client.launch_url + '/cookies')
      .maximizeWindow()
      .waitForElementVisible('body.cookies', 2000)
      .assert.containsText('h1', 'Cookies')
    ;
  },

  'Privacy/terms page': function(client) {
    client
      .init(client.launch_url + '/privacy')
      .maximizeWindow()
      .waitForElementVisible('body.privacy', 2000)
      .assert.containsText('h1', 'Terms and conditions and privacy')
    ;
  },

  'Feedback form page': function(client) {
    client
      .init(client.launch_url + '/feedback')
      .maximizeWindow()
      .waitForElementVisible('body.feedback', 2000)
      .assert.containsText('h1', 'Your feedback')
      .end()
    ;
  }

};
