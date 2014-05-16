module.exports = {
  "Conditional content" : function (browser) {
    browser
      .deleteCookies()
      .url(browser.launch_url + '/checker')
      .assert.containsText('h1', 'Your problem', 'page has correct title')
      .assert.hidden('.Conditional', 'conditional content not visible')
      .assert.elementPresent('input[name=your_problem-category]', 'option field exists')
      .execute(function () {
        $("input[name=your_problem-category][data-conditional-el]").attr("checked", true).trigger("change");
      })
      .waitForElementVisible('.Conditional', 500, 'wait for conditional content to show')
      .assert.visible('.Conditional', 'conditional content is visible')
      .execute(function () {
        $("input[name=your_problem-category]:not([data-conditional-el])").attr("checked", true).trigger("change");
      })
      .waitForElementNotVisible('.Conditional', 500, 'wait for conditional content to hide')
      .assert.hidden('.Conditional', 'conditional content not visible')
      .end();
  }
};
