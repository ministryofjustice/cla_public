'use strict';

var log = require('../modules/log');
var util = require('util');

exports.command = function(errorText, callback) {
  var client = this;
  errorText = errorText || 'This form has errors';

  this.perform(function() {
    log.command('Checking form validation…');

    client
      .submitForm('form', function() {
        console.log('     ⟡ Form submitted');
      })
      .waitForElementPresent('.alert-error', 5000, function() {
        console.log('    - Form has errors summary');
      })
      .assert.containsText('.alert-error', errorText)
      .execute(function(formErrorFields, errorSummaryItems, browserName) {
        return {
          formErrorCount: $(formErrorFields).filter(function() {
            // `submitForm` is not triggering form submit event in `form-errors when using PhantomJS
            // So we just check the error counts when form submitted via fallback not intercepted on client.
            if(browserName === 'phantomjs') {
              return true;
            }
            if($(this).hasClass('s-hidden') || $(this).parent().hasClass('s-hidden')) {
              return false;
            }
            return true;
          }).length,
          summaryItemCount: $(errorSummaryItems).length
        };
      }, ['.form-group.form-error', '.error-summary-details a', client.capabilities.browserName], function(result) {
        var value = result.value;
        this.assert.ok(value.formErrorCount > 0 && value.formErrorCount === value.summaryItemCount,
          util.format('Number of items in error summary (%s) matches number of form errors (%s)',
            value.summaryItemCount, value.formErrorCount));
      })
    ;
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
