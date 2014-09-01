(function () {
  'use strict';

  moj.Modules.FieldHelp = {
    el: '.js-FieldHelp',

    init: function () {
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function () {
      this.$options
        .on('focus', this.onFocus)
        .on('focusout', this.onFocusOut);
    },

    onFocus: function () {
      var $parent = $(this).parents('.FormRow');

      if ($parent.find('.Help-text').length > 0) {
        $parent.addClass('Help');
      }
    },

    onFocusOut: function () {
      $('.Help').removeClass('Help');
    },

    cacheEls: function () {
      this.$options = $(this.el).find('input[type=number], input[type=text], input[type=radio], input[type=checkbox], select');
    }
  };
}());