module.exports = {
  "Not eligible income w/ children (Your problem)": function (browser) {
    browser
      .deleteCookies()
      .url(browser.launch_url + '/checker')
      .assert.containsText('.PageHeader h1', 'Your problem', 'checker starts on correct page')
      .useXpath()
      .click('//*[@id="id_your_problem-category_0"]')
      .useCss()
      .submitForm('#content form');
  },
  
  "Not eligible income w/ children (Your details)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your details', 'your problem passes')
      .execute(function () {
        $("input[value=0][type=radio]").click();
        $("#id_your_details-has_children_0").click();
      })
      .submitForm('#content form');
  },
  
  "Not eligible income w/ children (Your finances - property)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your finances', 'your finances passes')
      .execute(function () {
        $("input[type=number]").val(0);
      })
      .submitForm('#content form');
  },
  
  "Not eligible income w/ children (Your finances - income)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your income', 'your income passes')
      .execute(function () {
        $("input[type=number]").val(0);
        $("#id_your_income-earnings").val(733.01+(285.13*3));
        $("input[value=1][type=radio]").click();
        $("#id_dependants-dependants_old").val(2);
        $("#id_dependants-dependants_young").val(1);
      })
      .submitForm('#content form');
  },
  
  "Not eligible income w/ children (Your finances - expenses)" : function (browser) {
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
