(function () {
  'use strict';

  moj.Modules.Shame = {
    init: function () {
      // Polyfill a given set of elements
      $('details').details();
      $('body').addClass($.fn.details.support ? 'details' : 'no-details');

      this.bindEvents();
    },

    bindEvents: function () {
      $(':input[type=number]').on('mousewheel',function() {
        $(this).blur();
      });
    }
  };
}());