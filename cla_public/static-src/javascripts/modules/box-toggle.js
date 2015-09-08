(function() {
  'use strict';

  moj.Modules.BoxToggle = {
    el: '[data-toggle-box]',

    init: function() {
      this.cacheEls();
      this.bindEvents();
    },

    cacheEls: function() {
      this.$toggleElements = $(this.el);
    },

    bindEvents: function() {
      var self = this;
      this.$toggleElements.each(function() {
        var $toggleElement = $(this);
        var context = {
          $toggleElement: $toggleElement,
          $targetElement: $($toggleElement.data("toggle-box"))
        };
        $toggleElement.on('click', $.proxy(self.toggleElement, context));
      });
    },

    toggleElement: function(event) {
      // NB: *this* is bound to a special context created in bindEvents

      event.preventDefault();
      this.$toggleElement.toggleClass("s-expanded");
      this.$targetElement.toggleClass("s-hidden");
    }
  };
}());
