module.exports = {
  "Start page" : function (browser) {
    browser
      .url(browser.launch_url)
      .assert.containsText('h1', 'Do you qualify for legal aid', 'contains correct title')
      .assert.elementPresent('a[role=button]', 'contains start button')
      .assert.containsText('a[role=button]', 'Continue', 'button contains correct text')
      .click('a[role=button]');
  },

  "Threshold page" : function (browser) {
    browser
      .assert.containsText('h1', 'Can you get legal aid', 'contains correct title')
      .assert.elementPresent('a[role=button]', 'contains start button')
      .assert.containsText('a[role=button]', 'Start', 'button contains correct text')      
      .end();
  }
};
