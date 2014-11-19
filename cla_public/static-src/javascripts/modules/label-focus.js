(function () {
  'use strict';

  moj.Modules.LabelFocus = {
    el: '.block-label',

    init: function () {
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function () {
      // set focused selector to parent label
      this.$options
        .on('focus', function () {
          $(this).parent('label').addClass('s-focused');
        })
        .on('focusout', function () {
          $('.s-focused').removeClass('s-focused');
        });
    },

    cacheEls: function () {
      this.$options = $(this.el).find('input[type=radio], input[type=checkbox]');
    }
  };
}());
