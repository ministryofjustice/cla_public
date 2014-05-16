module.exports = {
  "Subtotal Calculator" : function (browser) {
    browser
      .url(browser.launch_url)
      .assert.title('Civil Legal Advice')
      .end();
  }
};
