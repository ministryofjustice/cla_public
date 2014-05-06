/* globals _ */

(function () {
  'use strict';

  moj.Modules.Conditional = {
    el: '.js-Conditional',

    init: function () {
      _.bindAll(this, 'render');
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function () {
      this.$conditionals.on('change deselect', this.toggle);
      moj.Events.on('render', this.render);
    },

    cacheEls: function () {
      this.$conditionals = $(this.el);
    },

    render: function () {
      this.$conditionals.each(this.toggle);
    },

    toggle: function (e) {
      var $el = $(this),
          $conditionalEl = $('#' + $el.data('conditionalEl'));

      // trigger a deselect event if a change event occured
      if (e.type === 'change') {
        $('input[name="' + $el.attr('name') + '"]').not($el).trigger('deselect');
      }

      // if a conditional element has been set, run the checks
      if ($el.data('conditionalEl')) {
        $el.attr('aria-control', $el.data('conditionalEl'));

        // if checked show/hide the extra content
        if($el.is(':checked')){
          $conditionalEl.show();
          $conditionalEl.attr('aria-expanded', 'true').attr('aria-hidden', 'false');
        } else {
          $conditionalEl.hide();
          $conditionalEl.attr('aria-expanded', 'false').attr('aria-hidden', 'true');
        }
      }
    }
  };
}());