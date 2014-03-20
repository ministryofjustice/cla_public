(function () {
  'use strict';

  moj.Modules.LabelFocus = {
    el: 'form',

    init: function () {
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function () {
      // set focused selector to parent label
      this.$options
        .on('focus', function () {
          $(this).parent('label').addClass('is-focused');
        })
        .on('focusout', function () {
          $('.is-focused').removeClass('is-focused');
        });
    },

    cacheEls: function () {
      this.$options = $(this.el).find('input[type=radio], input[type=checkbox]');
    }
  };
}());