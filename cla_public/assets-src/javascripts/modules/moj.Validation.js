// Validation module
// Dependencies: moj, _, jQuery

(function () {
  'use strict';

  moj.Modules.Validation = {
    selector: '.ErrorSummary[role=alert]',

    init: function () {
      _.bindAll(this, 'render');
      this.bindEvents();
      this.render(null, {wrap: 'body'});
    },

    bindEvents: function () {
      moj.Events.on('Validation.render', this.render);
      $('body').on('click.moj.Modules.Validation', '[role="alert"] a', moj.Helpers.scrollTo);
    },

    render: function (e, params) {
      var $el = $(this.selector, $(params.wrap));

      if ($el.length > 0) {
        $el.focus();
      }
    }
  };

})();