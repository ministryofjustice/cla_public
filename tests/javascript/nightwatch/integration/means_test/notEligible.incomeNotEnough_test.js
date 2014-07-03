module.exports = {
  "Not eligible income (Your problem)": function (browser) {
    browser
      .deleteCookies()
      .url(browser.launch_url + '/checker')
      .assert.containsText('.PageHeader h1', 'Your problem', 'checker starts on correct page')
      .useXpath()
      .click('//*[@id="id_your_problem-category_0"]')
      .useCss()
      .submitForm('#content form');
  },
  
  "Not eligible income (Your details)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your details', 'your problem passes')
      .execute(function () {
        $("input[value=0][type=radio]").click();
      })
      .submitForm('#content form');
  },
  
  "Not eligible income (Your finances - property)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your finances', 'your finances passes')
      .execute(function () {
        $("input[type=number]").val(0);
      })
      .click('#content form button[type=submit]')
      .pause(2000);
  },
  
  "Not eligible income (Your finances - income)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your income', 'your income passes')
      .execute(function () {
        $("input[type=number]").val(0);
        $("#id_your_income-earnings_0").val(910.51);
        $("input[value=1][type=radio]").click();
      })
      .submitForm('#content form');
  },
  
  "Not eligible income (Your finances - expenses)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your expenses', 'your expenses passes')
      .execute(function () {
        $("input[type=number]").val(0);
      })
      .submitForm('#content form');
  },
  
  "Not eligible income Result" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'You are not able to get Legal Aid', 'result page contains unsuccessful title')
      .end();
  }
};
