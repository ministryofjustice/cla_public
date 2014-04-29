module.exports = {
  "Basic test" : function (browser) {
    browser
      .url(browser.launch_url)
      .assert.title('Civil Legal Advice')
      .end();
  }
};
