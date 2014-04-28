module.exports = {
  "Basic test" : function (browser) {
    browser
      .url("http://localhost:8002")
      .assert.title('Civil Legal Advice')
      .end();
  }
};
