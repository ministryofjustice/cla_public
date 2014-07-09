module.exports = {
  setUp : function(browser) {
    browser.capabilities['name'] = 'Details tag';
  },

  "Details tag" : function (browser) {
    browser
      .deleteCookies()
      .url(browser.launch_url + '/checker')
      .assert.containsText('h1', 'Your problem', 'page has correct title')
      .assert.elementPresent('details', 'details tag exists')
      .assert.hidden('details > div', 'details content not visible')
      .execute(function () {
        $("details:first").find('summary').click().trigger('click');
      })
      .assert.visible('details > *', 'details content is visible')
      .end();
  }
};
