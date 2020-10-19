 'use strict';
  var currencyValidation = require('./currencyInputValidation');
  var _ = require('lodash');
  moj.Modules.FormErrors = {
    init: function() {
      _.bindAll(this, 'postToFormErrors', 'onAjaxSuccess', 'onAjaxError');
      this.bindEvents();
      this.loadTemplates();
    },

    bindEvents: function() {
      $('form')
        .on('submit', this.postToFormErrors)
        // Focus back on summary if field-error is focused and escape key is pressed
        .on('blur', '.form-group', function(e) {
          $(e.target).removeAttr('tabindex');
        });

      $('[type=submit]').on('click', function(e) {
        var $target = $(e.target);
        $target.closest('form').attr('submit-name', $target.attr('name'));
      });
    },

    postToFormErrors: function(e) {
      this.$form = $(e.target);

      // Return if button has a name, which is attached as form attribute on click
      // (assuming secondary buttons)
      if(this.$form.attr('submit-name') ||
         this.$form.attr('method') && this.$form.attr('method').toLowerCase() === 'get') {
        return;
      }

      if (this.$form.length) {
        e.preventDefault();
        e.stopPropagation();
        $.ajax({
          type: 'POST',
          url: this.$form.attr('action'),
          contentType: 'application/x-www-form-urlencoded',
          data: this.$form.serialize()
        })
        .done(this.onAjaxSuccess)
        .fail(this.onAjaxError);
      }
    },

    onAjaxSuccess: function(data) {
      if (data.redirect) {
        window.location.href = data.redirect;
      }
      if (data.field_errors) {
        this.loadErrors(data.field_errors);
        var errorBanner = $('.govuk-error-summary:visible:first');

        if(!errorBanner.length) {
          return;
        }

        $('html, body').animate({
          scrollTop: errorBanner.offset().top - 20
        }, 300, function() {
          errorBanner.attr({'tabindex': -1}).focus();
        });
      }
      if (data.non_field_errors.length) {
        $('#non-field-error-ajax .alert-message').text(data.non_field_errors[0]);
        $('#non-field-error-ajax').show();
      }
      else {
        $('#non-field-error-ajax').hide();
      }
    },

    onAjaxError: function() {
      this.$form.off('submit');
      this.$form.submit();
    },

    formatErrors: function(errors) {
      var errorFields = {};

      (function fieldName (errorsObj, prefix) {
        prefix = (typeof prefix === 'undefined') ? '' : prefix + '-';
        for (var key in errorsObj) {
          var field = prefix + key;
          if ($.isArray(errorsObj[key])) {
            errorFields[field] = errorsObj[key];
          } else {
            fieldName(errorsObj[key], field);
          }
        }
      })(errors);

      return errorFields;
    },

    createErrorSummary: function(unattachedErrors) {
      var errorSummary = [];

      // Loop through errors on the page to retain the fields order
      $('.govuk-form-group--error, .govuk-form-group--error>fieldset').map(function() {
        var $this = $(this);

        if(!this.id || $this.hasClass('s-hidden') || $this.parent().hasClass('s-hidden')) {
          return;
        }
        var name = this.id.replace(/^field-/, '');

        var labelField = $this.find('#field-label-' + name);

        var errorText = $this.find('#error-' + name + " .cla-error-message").text();

        $this.find(' .govuk-input')
          .not('.govuk-form-group--error .govuk-radios__conditional .govuk-input')
          .addClass("govuk-input--error")
          .focus(function() {
            $this.find('.laa-currency .govuk-input.govuk-input--error').siblings(".laa-currency-prefix")
            .removeClass("laa-currency-prefix--error")
          })
          .blur(function() {
            $this.find('.laa-currency .govuk-input.govuk-input--error').siblings(".laa-currency-prefix")
            .addClass("laa-currency-prefix--error");
          });
        $this.find(' .govuk-select')
          .not('.govuk-form-group--error .govuk-radios__conditional .govuk-select')
          .addClass("govuk-select--error");

        if (labelField.parents(".cla-currency-by-frequency").length) {
          labelField = labelField.parents(".cla-currency-by-frequency").children("legend");

          var inputElementWithValidEntry = $this.find(' .govuk-input').filter(function () {
            return currencyValidation.isValidAmount($(this).val())
          })

          if(!inputElementWithValidEntry.length) {
            $this.find(' .govuk-input')
            .focus(function() {
              $this.find('.laa-currency .govuk-input.govuk-input--error').siblings(".laa-currency-prefix")
              .removeClass("laa-currency-prefix--error")
            })
            .blur(function() {
              $this.find('.laa-currency .govuk-input.govuk-input--error').siblings(".laa-currency-prefix")
              .addClass("laa-currency-prefix--error");
            })
          }

          inputElementWithValidEntry
          .removeClass("govuk-input--error")

          $this.find(' .govuk-select').filter(function () {
            return ($(this).val())
          })
          .removeClass("govuk-select--error")

        }

        $this.find('.laa-currency .govuk-input.govuk-input--error').siblings(".laa-currency-prefix")
        .addClass("laa-currency-prefix--error");

        if (errorText) {
          var labelText = errorText;
        } else {
          var labelText = labelField.text().replace(/if yes, /i,"").replace(/os ydych, /i,"").replace(/os oes, /i,"").trim();
          //above lines are stripping the "if yes" (and Welsh variants) from the error summary.

          labelText = labelText.charAt(0).toUpperCase() + labelText.substr(1);
          //Ensures the first letter is uppercase.
        }

        errorSummary.push({
          label: labelText,
          name: name,
          errors: $this.find('> .govuk-error-message > .cla-error-message').map(function() {
            return $(this).text();
          })
        });
      });

      _.each(unattachedErrors, function(error) {
        errorSummary.push({
          errors: [error]
        });
      });

      return errorSummary;
    },

    loadErrors: function(errors) {
      var errorFields = this.formatErrors(errors);
      var self = this;
      var unattachedErrors = [];

      this.clearErrors();

      function insertError($afterElement, errors, fieldName) {
        $afterElement.after(self.fieldError({
          errors: errors,
          fieldName: fieldName
        }));
      }

      function addSimpleErrors(errors, fieldName) {
        if(!errors.length) {
          return;
        }

        $('#field-' + fieldName)
          .attr({
            'aria-invalid': true,
            'aria-describedby': 'error-' + fieldName
          })
          .closest('.govuk-form-group').addClass('govuk-form-group--error');

        var label = $('#field-label-' + fieldName);

        if (label.parents(".cla-currency-by-frequency").length) {
          label = label.parents(".cla-currency-by-frequency").children("legend");
        }

        if(!label.length) {
          unattachedErrors = _.extend(unattachedErrors, errors);
        } else if(label.parent().children('.govuk-hint').length) {
          insertError(label.parent().children('.govuk-hint'), errors, fieldName);
        } else if(label.is('legend')) {
          insertError(label, errors, fieldName);
        } else {
          insertError(label.closest('.govuk-label'), errors, fieldName);
        }
      }

      function addSubformErrors(errors, fieldName) {
        if(!errors.length) {
          return;
        }
        _.each(errors, function(subformErrors) {
          addErrors(subformErrors[1], fieldName + '-' + subformErrors[0]);
        });
      }

      function addRepeatedFieldErrors(errors, fieldName) {
        if(!errors.length) {
          return;
        }
        // Multiple forms (e.g. properties)
        _.each(errors, function(errors) {
          _.each(errors._errors, function(subformErrors, subformFieldName) {
            addErrors(subformErrors, fieldName + '-' + errors._index + '-' + subformFieldName);
          });
        });
      }

      function addErrors(errors, fieldName) {
        addSimpleErrors(_.filter(errors, _.isString), fieldName);
        addSubformErrors(_.filter(errors, _.isArray), fieldName);
        addRepeatedFieldErrors(_.filter(errors, function(error) {
          return _.isObject(error) && !_.isArray(error);
        }), fieldName);
      }

      _.each(errorFields, addErrors);

      if(this.$form.data('error-banner') !== false) {
        if ($(".s-hidden input").val()) {
          // In case a hidden field is throwing an error,
          $(".s-hidden input").val("");
          // we wipe the value,
          $("#submit-button").click();
          // and retry the submit.
        } else {
          this.$form.closest('main').prepend(this.mainFormError({ errors: this.createErrorSummary(unattachedErrors)}));
          if (GOVUK.getCookie("locale") == "cy_GB") {
            $("title").prepend("Gwall: ");
          } else {
            $("title").prepend("Error: ");
          }
        }
      }

      // Report to GA about form errors
      var errorFieldNames = _.keys(errorFields);
      if(!window.ga) {
        return;
      }
      window.ga('send', 'event', 'form-errors',
        window.location.pathname,
        errorFieldNames.join('|'),
        errorFieldNames.length
      );
    },

    loadTemplates: function() {
      this.mainFormError = _.template($('#mainFormError').html());
      this.fieldError = _.template($('#fieldError').html());
    },

    clearErrors: function() {
      $("title").text(
        $("title").text()
          .replace("Error: ", "")
          .replace("Gwall: ", "")
      );
      $('.govuk-error-message:not(.govuk-character-count__message )').remove();
      $('.govuk-error-summary').remove();
      $('.govuk-form-group--error')
        .removeClass('govuk-form-group--error')
        .removeAttr('aria-invalid');
      $(".govuk-input--error")
        .removeClass("govuk-input--error");
      $(".govuk-select--error")
        .removeClass("govuk-select--error");
      $(".laa-currency-prefix--error")
        .removeClass("laa-currency-prefix--error");
    }
  };
