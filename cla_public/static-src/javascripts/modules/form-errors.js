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
    },

    postToFormErrors: function(e) {
      this.clearErrors();
      this.$form = $(e.target);

      // Return if button has a name, which is attached as form attribute on click
      // (assuming secondary buttons)
      if(this.$form.attr('submit-name')) {
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
        $('html, body').animate({
          scrollTop: $('.alert-error:visible:first').offset().top - 50
        }, 300);
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

    loadErrors: function(errors) {
      var errorFields = this.formatErrors(errors);
      var self = this;

      function addErrors(errors, fieldName) {
        if (_.isString(errors[0])) {
          $('#field-' + fieldName).addClass('m-error');
          $('#field-label-' + fieldName)
            .addClass('m-error')
            .after(self.fieldError({ errors: errors }));
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

      this.$form.prepend(this.mainFormError());
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
