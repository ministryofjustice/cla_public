(function () {
  'use strict';

  moj.Modules.ConditionalSubfields = {
    subfields: [],

    init: function() {
      this.cacheEls();
      this.bindEvents();
      this.setInitialState();
      this.replaceLabels();
    },

    setInitialState: function() {
      var self = this;
      this.subfields.filter(function() {
        return $(this).is(':checked');
      }).each(function() {
        self.setVisibility($(this).data('controls'), this.value === '1');
      });
    },

    replaceLabels: function() {
      if(!window.CONDITIONAL_LABELS) {
        return;
      }

      var labelsToReplace = $.unique(
        $.map($(this.subfields), function(item) {
          return $(item).data('controls');
        })
      );

      // Find labels defined in template and replace the text.
      // Exclude the prefix/suffix labels
      $.each(labelsToReplace, function() {
        if(typeof window.CONDITIONAL_LABELS[this] !== 'string') {
          return;
        }

        $('label[for="' + this + '"]')
          .filter(function() {
            return !$(this).hasClass('input-prefix') && !$(this).hasClass('input-suffix');
          })
          .text(window.CONDITIONAL_LABELS[this]);
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
