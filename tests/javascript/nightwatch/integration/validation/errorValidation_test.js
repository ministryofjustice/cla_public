module.exports = {
  "Your problem fails" : function (browser) {
    browser
      .deleteCookies()
      .url(browser.launch_url + '/checker')
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'Your problem', 'remained on same page')
      .assert.elementPresent('.ErrorSummary', 'error summary is present')
      .assert.containsText('.ErrorSummary', 'There was a problem submitting the form', 'error summary contains correct message')
      .assert.elementPresent('.FormRow.Error', 'field errors are present');
  },

  "Your problem passes" : function (browser) {
    browser
      .execute(function () {
        $("input[name=your_problem-category]:first").click();
      })
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'Your finances', 'passes when completed')
  },

  "Your finances start page passes" : function (browser) {
    browser
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'About you', 'passes when completed')
  },

  "Your details fails" : function (browser) {
    browser
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'About you', 'remained on same page')
      .assert.elementPresent('.ErrorSummary', 'error summary is present')
      .assert.containsText('.ErrorSummary', 'There was a problem submitting the form', 'error summary contains correct message')
      .assert.elementPresent('.FormRow.Error', 'field errors are present')
      .assert.containsText('.FormRow.Error', 'cannot be blank', 'field error contains correct message');
  },

  "Your details passes" : function (browser) {
    browser
      .execute(function () {
        $("input[value=0][type=radio]").click();
      })
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'Your money', 'passes when completed')
  },

  "Your finances fails" : function (browser) {
    browser
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'Your money', 'remained on same page')
      .assert.elementPresent('.ErrorSummary', 'error summary is present')
      .assert.containsText('.ErrorSummary', 'There was a problem submitting the form', 'error summary contains correct message')
      .assert.elementPresent('.FormRow.Error', 'field errors are present')
      .assert.containsText('.FormRow.Error', 'cannot be blank', 'field error contains correct message');
  },

  "Your finances passes" : function (browser) {
    browser
      .execute(function () {
        $("input[type=number]").val(0);
        $("input[value=1][type=radio]").click();
      })
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'Your income', 'passes when completed')
  },

  "Your income fails" : function (browser) {
    browser
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'Your income', 'remained on same page')
      .assert.elementPresent('.ErrorSummary', 'error summary is present')
      .assert.containsText('.ErrorSummary', 'There was a problem submitting the form', 'error summary contains correct message')
      .assert.elementPresent('.FormRow.Error', 'field errors are present')
      .assert.containsText('.FormRow.Error', 'cannot be blank', 'field error contains correct message');
  },

  "Your income passes" : function (browser) {
    browser
      .execute(function () {
        $("input[type=number]").val(0);
      })
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'Your expenses', 'passes when completed')
  },

  "Your expenses fails" : function (browser) {
    browser
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'Your expenses', 'remained on same page')
      .assert.elementPresent('.ErrorSummary', 'error summary is present')
      .assert.containsText('.ErrorSummary', 'There was a problem submitting the form', 'error summary contains correct message')
      .assert.elementPresent('.FormRow.Error', 'field errors are present')
      .assert.containsText('.FormRow.Error', 'cannot be blank', 'field error contains correct message');
  },

  "Your expenses passes" : function (browser) {
    browser
      .execute(function () {
        $("input[type=number]").val(0);
      })
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'You might be able to get Legal Aid', 'passes when completed')
  },

  "Result fails" : function (browser) {
    browser
      .submitForm('#content form')
      .assert.containsText('.PageHeader h1', 'You might be able to get Legal Aid', 'remained on same page')
      .assert.elementPresent('.ErrorSummary', 'error summary is present')
      .assert.containsText('.ErrorSummary', 'There was a problem submitting the form', 'error summary contains correct message')
      .assert.elementPresent('.FormRow.Error', 'field errors are present')
      .assert.containsText('.FormRow.Error', 'cannot be blank', 'field error contains correct message');
  },

  "Result passes" : function (browser) {
    browser
      .setValue('[name=contact_details-full_name]', 'Test Name')
      .setValue('[name=contact_details-postcode]', 'SW1 1DD')
      .setValue('[name=contact_details-street]', 'Street')
      .setValue('[name=contact_details-mobile_phone]', '01234567890')
      .submitForm('#content form')
      .assert.containsText('.PageHeader p', 'Your reference number', 'passes when completed')
      .end();
  }
};
