(function() {
  'use strict';

  moj.Modules.FormErrors = {
    init: function() {
      _.bindAll(this, 'postToFormErrors', 'onAjaxSuccess', 'onAjaxError');
      this.bindEvents();
      this.loadTemplates();
    },

    bindEvents: function() {
      $('form').on('submit', this.postToFormErrors);
      $('[type=submit]').on('click', function(e) {
        var $target = $(e.target);
        $target.closest('form').attr('submit-name', $target.attr('name'));
      });

      $('#content').on('click', '.error-summary a', function(e) {
        e.preventDefault();
        $('fieldset').removeClass('s-targeted');
        var targetId = e.target.href.replace(/.*#/, '#');
        if(targetId.length < 2) {
          return;
        }
        var $target = $(targetId);
        $target.addClass('s-targeted');

        $('html, body').animate({
          scrollTop: $target.offset().top - 20
        }, 300, function() {
          $target.attr('tabindex', -1).focus();
        });
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
          type: 'OPTIONS',
          url: '',
          contentType: 'application/x-www-form-urlencoded',
          data: this.$form.serialize()
        })
        .done(this.onAjaxSuccess)
        .fail(this.onAjaxError);
      }
    },

    onAjaxSuccess: function(errors) {
      if (!$.isEmptyObject(errors)) {
        this.loadErrors(errors);
        var errorBanner = $('.alert-error:visible:first');

        if(!errorBanner.length) {
          return;
        }

        $('html, body').animate({
          scrollTop: errorBanner.offset().top - 20
        }, 300, function() {
          errorBanner.attr({'tabindex': -1}).focus();
        });
      } else {
        this.$form.off('submit');
        this.$form.submit();
      }
    },

    onAjaxError: function() {
      this.$form.off('submit');
      this.$form.submit();
    },

    formatErrors: function(errors) {
      var errorFields = {};

      (function fieldName (errorsObj, prefix) {
        prefix = (typeof prefix === 'undefined')? '': prefix + '-';
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

    createErrorSummary: function() {
      var errorSummary = [];

      // Loop through errors on the page to retain the fields order
      $('fieldset.m-error').map(function() {
        var $this = $(this);

        if(!this.id || $this.hasClass('s-hidden') || $this.parent().hasClass('s-hidden')) {
          return;
        }
        var name = this.id.replace(/^field-/, '');

        errorSummary.push({
          label: $this.find('> .fieldset-label').text(),
          name: name,
          errors: $this.find('> .field-error p').map(function() {
            return $(this).text();
          })
        });
      });

      return errorSummary;
    },

    loadErrors: function(errors) {
      var errorFields = this.formatErrors(errors);
      var self = this;

      this.clearErrors();

      function addErrors(errors, fieldName) {
        if (_.isString(errors[0])) {
          $('#field-' + fieldName).addClass('m-error');
          var label = $('#field-label-' + fieldName).addClass('m-error');
          label.after(self.fieldError({ errors: errors }));
        } else if(_.isObject(errors[0]) && !_.isArray(errors[0])) {
          // Multiple forms (e.g. properties)
          _.each(errors, function(errors, i) {
            _.each(errors, function(subformErrors, subformFieldName) {
              addErrors(subformErrors, fieldName + '-' + i + '-' + subformFieldName);
            });
          });
        } else {
          _.each(errors, function(subformErrors) {
            addErrors(subformErrors[1], fieldName + '-' + subformErrors[0]);
          });
        }
      }

      _.each(errorFields, addErrors);

      if(this.$form.data('error-banner') !== false) {
        this.$form.prepend(this.mainFormError({ errors: this.createErrorSummary()}));
      }
    },

    loadTemplates: function() {
      this.mainFormError = _.template($('#mainFormError').html());
      this.fieldError = _.template($('#fieldError').html());
    },

    clearErrors: function() {
      $('.form-row.field-error').remove();
      $('.alert.alert-error').remove();
      $('.m-error').removeClass('m-error');
    }
  };
}());
