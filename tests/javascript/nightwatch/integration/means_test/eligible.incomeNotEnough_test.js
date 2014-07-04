module.exports = {
  "Eligible income (Your problem)": function (browser) {
    browser
      .deleteCookies()
      .url(browser.launch_url + '/checker')
      .assert.containsText('.PageHeader h1', 'Your problem', 'checker starts on correct page')
      .useXpath()
      .click('//*[@id="id_your_problem-category_0"]')
      .useCss()
      .submitForm('#content form');
  },
  
  "Eligible income (Your finances start page)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your finances', 'your problem start page contains correct title')
      .submitForm('#content form');
  },
  
  "Eligible income (Your details)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'About you', 'your details contains correct title')
      .execute(function () {
        $("input[value=0][type=radio]").click();
        $("#id_your_details-has_partner_0").click();
      })
      .submitForm('#content form');
  },
  
  "Eligible income (Your finances - property)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your money', 'your property contains correct title')
      .execute(function () {
        $("input[type=number]").val(0);
      })
      .submitForm('#content form');
  },
  
  "Eligible income (Your finances - income)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your income', 'your income contains correct title')
      .execute(function () {
        $("input[type=number]").val(0);
        $("#id_your_income-earnings_0").val(910.5);
        $("input[value=1][type=radio]").click();
      })
      .submitForm('#content form');
  },
  
  "Eligible income (Your finances - expenses)" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'Your expenses', 'your expenses contains correct title')
      .execute(function () {
        $("input[type=number]").val(0);
      })
      .submitForm('#content form');
  },
  
  "Eligible income Result" : function (browser) {
    browser
      .assert.containsText('.PageHeader h1', 'You might be able to get Legal Aid', 'result page contains successful title')
      .assert.containsText('#content button[type=submit]', 'Apply for legal aid', 'result page contains apply button')
      .setValue('[name=contact_details-full_name]', 'Test Name')
      .setValue('[name=contact_details-postcode]', 'SW1 1DD')
      .setValue('[name=contact_details-street]', 'Street')
      .setValue('[name=contact_details-mobile_phone]', '01234567890')
      .submitForm('#content form');
  },
  
  "Eligible income Confirmation" : function (browser) {
    browser
      .assert.containsText('.PageHeader p', 'Your reference number', 'confirmation page contains reference number')
      .end();
  }
};
