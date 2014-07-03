module.exports = {
  "Subtotal Calculator - Get to expenses step": function (browser) {
    browser
      .deleteCookies()
      .url(browser.launch_url + '/checker')
      .useXpath()
      .click('//*[@id="id_your_problem-category_0"]')
      .useCss()
      .submitForm('#content form')
      .execute(function () {
        $("input[value=0][type=radio]").click();
        $("#id_your_details-has_partner_0").click();
      })
      .submitForm('#content form')
      .execute(function () {
        $("input[type=number]").val(0);
      })
      .click('#content form button[type=submit]')
      .pause(2000)
      .execute(function () {
        $("input[type=number]").val(0);
        $("#id_your_income-earnings").val(910.5);
        $("input[value=1][type=radio]").click();
      })
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'Your expenses', 'on correct page for calculator');
  },

  "Subtotal Calculator" : function (browser) {
    browser
      .assert.visible('.SubTotal', 'sub total containers are present')
      .execute(function () {
        $("#id_your_allowances-mortgage_0").val(50).keyup();
      })
      .useXpath()
      .assert.containsText('//*[@id="content"]/div/form/section[1]/div/p/span', '£ 50.00', 'first total calculated the correct value')
      .assert.containsText('//*[@id="content"]/div/form/section[2]/div/p/span', '£ 0.00', 'second total remained at 0')
      .execute(function () {
        $("#id_partners_allowances-mortgage_0").val(75).keyup();
        $("#id_partners_allowances-rent_0").val(150).keyup();
      })
      .assert.containsText('//*[@id="content"]/div/form/section[1]/div/p/span', '£ 50.00', 'first total remained the same')
      .assert.containsText('//*[@id="content"]/div/form/section[2]/div/p/span', '£ 225.00', 'second total calculated the correct value')
      .end();
  }
};
