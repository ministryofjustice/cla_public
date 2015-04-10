'use strict';

module.exports = {
  '404 page': function(client) {
    client
      .deleteCookies()
      .init(client.launch_url + '/notfound')
      .maximizeWindow()
      .waitForElementVisible('body', 5000)
      .assert.containsText('h1', 'Sorry, this page doesn’t exist')
      .end()
    ;
  }
};
