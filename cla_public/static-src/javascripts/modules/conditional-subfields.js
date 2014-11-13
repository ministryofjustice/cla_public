(function () {
  'use strict';

  moj.Modules.ConditionalSubfields = {
    subfields: [],

    init: function() {
      this.cacheEls();
      this.bindEvents();
      this.setInitialState();
    },

    setInitialState: function() {
      var self = this;
      this.subfields.filter(function() {
        return $(this).is(':checked');
      }).each(function() {
        self.setVisibility($(this).data('controls'), this.value === '1');
      });
    },

    bindEvents: function() {
      this.subfields
        .on('change', $.proxy(this.handleChange, this));
    },

    handleChange: function(evt) {
      var $el = $(evt.target);
      var isShown = !!parseInt($el.val());
      var id = $el.data('controls');

      this.setVisibility(id, isShown);
    },

    setVisibility: function(subfieldId, visibility) {
      $('[data-subfield-id="' + subfieldId +'"]')
        .toggleClass('s-expanded', visibility)
        .toggleClass('s-hidden', !visibility);
    },

    cacheEls: function() {
      this.subfields = $('[data-controls]');
    }
  };
}());
