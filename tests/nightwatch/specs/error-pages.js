'use strict';

module.exports = {
  '404 page': function(client) {
    client
      .init(client.launch_url + '/qwertyuiopasdfghjklzxcvbnm')
      .maximizeWindow()
      .waitForElementVisible('body', 1000)
      .assert.containsText('h1', 'Sorry, this page doesn’t exist')
      .end()
    ;
  }

};
