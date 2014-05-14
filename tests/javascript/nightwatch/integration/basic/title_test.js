module.exports = {
  "Site" : function (browser) {
    browser
      .url(browser.launch_url)
      .assert.title('Civil Legal Advice', 'contains correct page title')
      .end();
  }
};
