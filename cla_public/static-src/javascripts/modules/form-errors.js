(function () {
  'use strict';

  moj.Modules.FormErrors = {
    init: function() {
      this.bindEvents();
    },

    bindEvents: function() {
      $('form').on('submit',  $.proxy(this.postToFormErrors, this));
    },

    postToFormErrors: function(e) {
      var $form = $(e.currentTarget);
      var self = this;
      $.ajax({
        type: 'OPTIONS',
        url: '',
        contentType: "application/x-www-form-urlencoded",
        data: $form.serialize(),
        async: false,
        success: function(errors) {
          if (!$.isEmptyObject(errors)) {
            e.preventDefault();
            e.stopPropagation();
            self.loadErrors(errors);
          }
        }
      });
    },

    loadErrors: function (errors) {
      var errorFields = {};

      (function fieldName (errorsObj, prefix) {
        prefix = (typeof prefix == 'undefined')? '': prefix + '-';
        for (var key in errorsObj) {
          var field = prefix + key;
          if ($.isArray(errorsObj[key])) {
            errorFields[field] = errorsObj[key];
          } else {
            fieldName(errorsObj[key], field);
          }
        }
      })(errors);

      for (var id in errorFields) {
        $('#field-' + id).addClass('m-error');
        $('#field-label-' + id).addClass('m-error');
      }


    }
  };
}());
