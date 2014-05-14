module.exports = {
  "Details tag" : function (browser) {
    browser
      .url(browser.launch_url)
      .assert.title('Civil Legal Advice')
      .end();
  }
};
