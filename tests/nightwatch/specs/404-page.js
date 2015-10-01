'use strict';

module.exports = {
  '404 page': function(client) {
    client
      .deleteCookies()
      .init(client.launch_url + '/notfound')
      .maximizeWindow()
      .ensureCorrectPage('body', '/notfound', {
        'h1': 'Sorry, this page doesn’t exist'
      })
      .end()
    ;
  }
};
