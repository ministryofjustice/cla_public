module.exports = {
  "Conditional content" : function (browser) {
    browser
      .url(browser.launch_url)
      .assert.title('Civil Legal Advice')
      .end();
  }
};
