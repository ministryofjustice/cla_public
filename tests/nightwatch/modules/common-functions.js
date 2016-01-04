'use strict';

var util = require('util');
var _ = require('lodash');
var SAVINGS_QUESTIONS = require('../modules/constants').SAVINGS_QUESTIONS;
SAVINGS_QUESTIONS.ALL = SAVINGS_QUESTIONS.MONEY.concat(SAVINGS_QUESTIONS.VALUABLES);

module.exports = {
  setAllSavingsFieldsToValue: function(client, val) {
    SAVINGS_QUESTIONS.ALL.forEach(function(item) {
      client
        .clearValue(util.format('input[name="%s"]', item.name))
        .setValue(util.format('input[name="%s"]', item.name), val)
      ;
    });
  },

  // check specific field group for error text
  submitAndCheckForFieldError: function(client, fields, tag) {
    tag = tag || "input";

    client
      .submitForm('form', function() {
        console.log('     ⟡ Form submitted');
      })
      .waitForElementPresent('.alert-error', 3000,
        '    - Form has errors summary')
      .useXpath()
    ;
    fields.forEach(function(field) {
      client.assert.containsText(util.format('//%s[@name="%s"]/ancestor::*[contains(@class, "form-group")]', tag, field.name), field.errorText,
        util.format('    - `%s` has error message: `%s`', field.name, field.errorText));
    });
    client.useCss();
  },

  checkAttributeIsNotPresent: function(client, selector, attribute) {
    client
      .getAttribute(selector, attribute, function(result) {
        this.assert.equal(result.value, null, util.format('Checking selector %s does NOT have attribute %s: %s', selector, attribute, (result.value === null)));
      })
    ;
  },

  humaniseValue: function(value) {
    var yesNo = {
      '1': 'Yes',
      '0': 'No'
    };

    return yesNo[value] || value;
  },

  formatMoneyInputs: function(prefix, inputs) {
    var result = {};
    _.each(inputs, function(v, k) {
      if(_.isObject(v)) {
        _.map(v, function(value, period) {
          result[util.format('%s%s-per_interval_value', prefix, k)] = value;
          result[util.format('%s%s-interval_period', prefix, k)] = period;
        });
      } else {
        result[util.format('%s%s', prefix, k)] = v;
      }
    });
    return result;
  },

  fillInMoneyForm: function(client, inputs, type) {
    _.each(inputs, function(v, k) {
      var selector = util.format('[name="%s"]', k);
      client.elements('css selector', selector, function(result) {
        if(!result.value.length) {
          return;
        }

        if(typeof v === 'number') {
          client
            .clearValue(selector)
            .setValue(selector, v, function() {
              console.log('     • %s: %s is £%d', type, k, v);
            });
        } else {
          selector += util.format(' [value="%s"]', v);
          client.click(selector, function() {
            console.log('       • %s selected', v);
          });
        }
      });
    });
  }
};
