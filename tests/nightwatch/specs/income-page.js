'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var constants = require('../modules/constants');

var EMPLOYMENT_QUESTIONS = constants.EMPLOYMENT_QUESTIONS;
EMPLOYMENT_QUESTIONS.EMPLOYED = EMPLOYMENT_QUESTIONS.EMPLOYED_MANDATORY.concat(EMPLOYMENT_QUESTIONS.EMPLOYED_OPTIONAL);
EMPLOYMENT_QUESTIONS.ALL = EMPLOYMENT_QUESTIONS.EMPLOYED.concat(EMPLOYMENT_QUESTIONS.COMMON);

var other_income_amount = 'input[name="your_income-other_income-per_interval_value"]';

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis(constants.SCOPE_PATHS.debtInScope);
  },

  'Interstitial page': function(client) {
    client.interstitialPage();
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true);
  },

  'Income': function(client) {
    client.ensureCorrectPage('input[name="your_income-other_income-per_interval_value"]', '/income', {
      'h1': 'Your money'
    });
  },

  'Context-dependent questions for employment status': function(client) {
    client
      .back()
      .waitForElementVisible('#have_partner-0', 5000,
        '  - Back to /about'
      )
      .setYesNoFields('is_employed', 1)
      .conditionalFormSubmit(true)
    ;
    EMPLOYMENT_QUESTIONS.EMPLOYED.forEach(function(item) {
      client
        .assert.visible(util.format('[name="your_income-%s-per_interval_value"]', item),
          util.format('    - `your_income-%s-per_interval_value` is visible', item)
        )
      ;
    });

    client
      .back()
      .waitForElementVisible('#have_partner-0', 5000,
        '  - Back to /about'
      )
      .setYesNoFields('is_employed', 0)
      .setYesNoFields('is_self_employed', 1)
      .conditionalFormSubmit(true)
    ;
    EMPLOYMENT_QUESTIONS.EMPLOYED.forEach(function(item) {
      client
        .assert.visible(util.format('[name="your_income-%s-per_interval_value"]', item),
          util.format('    - `your_income-%s-per_interval_value` is visible', item)
        )
      ;
    });
  },

  'Context-dependent text and questions for partner': function(client) {
    EMPLOYMENT_QUESTIONS.EMPLOYED.concat(EMPLOYMENT_QUESTIONS.COMMON).forEach(function(item) {
      client
        .assert.elementNotPresent(util.format('[name="partner_income-%s-per_interval_value"]', item),
          util.format('    - `partner_income-%s-per_interval_value` is not present', item)
        )
      ;
    });

    client
      .back()
      .waitForElementVisible('#have_partner-0', 5000,
        '  - Back to /about'
      )
      .setYesNoFields('have_partner', 1)
      .setYesNoFields(['in_dispute', 'is_self_employed', 'partner_is_self_employed'], 0)
      .setYesNoFields('partner_is_employed', 1)
      .conditionalFormSubmit(true)
      .assert.containsText('h1', 'You and your partner’s money',
        '    - Page heading is correct'
      )
      .assert.containsText('form fieldset:nth-of-type(1) header', 'Your money',
        '    - Your money section is present'
      )
      .assert.containsText('form fieldset:nth-of-type(2) header', 'Your partner’s money',
        '    - Your partner’s money section is present'
      )
    ;
    EMPLOYMENT_QUESTIONS.COMMON.forEach(function(item) {
      client
        .assert.visible(util.format('[name="partner_income-%s-per_interval_value"]', item),
          util.format('    - `partner_income-%s-per_interval_value` is visible', item)
        )
      ;
    });
    client
      .back()
      .waitForElementVisible('#have_partner-0', 5000,
        '  - Back to /about'
      )
      .setYesNoFields('is_employed', 1)
      .conditionalFormSubmit(true)
    ;
    EMPLOYMENT_QUESTIONS.EMPLOYED.forEach(function(item) {
      client
        .assert.visible(util.format('[name="partner_income-%s-per_interval_value"]', item),
          util.format('    - `partner_income-%s-per_interval_value` is visible', item)
        )
      ;
    });
  },

  'Test validation': function(client) {
    client.ensureFormValidation();

    function checkForErrors(fields, errorText, includePartner) {
      var persons = ['your'];

      if(includePartner) {
        persons.push('partner');
      }

      client.useXpath();

      persons.map(function(person) {
        fields.map(function (field) {
          var fieldName = util.format('%s_income-%s-per_interval_value', person, field);
          client.assert.containsText(util.format('//*[@name="%s"]/ancestor::*[contains(@class, "form-group")]', fieldName), errorText,
            util.format('    - `%s` has error message: `%s`', fieldName, errorText));
        });
      });

      client.useCss();
    }

    function setValues(fields, suffix, value, includePartner) {
      var persons = ['your'];

      if(includePartner) {
        persons.push('partner');
      }

      persons.map(function (person) {
        fields.map(function (field) {
          var fieldName = util.format('%s_income-%s-%s', person, field, suffix);

          if(suffix === 'interval_period') {
            client.selectDropdown(fieldName, value);
          } else {
            client.setValue(util.format('[name=%s]', fieldName), value, function () {
              console.log(util.format('       • %s set to %s', fieldName, value));
            });
          }
        })
      });
    }

    checkForErrors(EMPLOYMENT_QUESTIONS.EMPLOYED_MANDATORY, 'Please provide an amount', true);
    checkForErrors(['working_tax_credit', 'maintenance', 'pension', 'other_income'], 'Enter 0 if this doesn’t apply to you', true);

    setValues(EMPLOYMENT_QUESTIONS.ALL, 'per_interval_value', 250, true);

    client.ensureFormValidation();

    checkForErrors(EMPLOYMENT_QUESTIONS.ALL, 'Please select a time period from the drop down', true);
    setValues(EMPLOYMENT_QUESTIONS.ALL, 'interval_period', 'per_month', true);

    client
      .conditionalFormSubmit(true)
      .end()
    ;
  }

};
