(function () {
  'use strict';

  moj.Modules.ConditionalSubfields = {
    el: '[data-conditional-controls]',

    init: function() {
      this.cacheEls();
      this.bindEvents();
      this.setInitialState();
      this.replaceLabels();
    },

    setInitialState: function() {
      var self = this;
      this.subfields
        .filter(function() {
          // Unchecked checkbox or checked radio button
          return this.type === 'checkbox' || $(this).is(':checked');
        })
        .each(function() {
          self.setVisibility($(this));
        });
      },

    replaceLabels: function() {
      if(!window.CONDITIONAL_LABELS) {
        return;
      }

      var labelsToReplace = $.unique(
        $.map($(this.subfields), function(item) {
          return $(item).data().conditionalControls;
        })
      );

      // Find labels defined in template and replace the text.
      // Exclude the prefix/suffix labels
      $.each(labelsToReplace, function() {
        if(typeof window.CONDITIONAL_LABELS[this] !== 'string') {
          return;
        }

        // Use 'begins with' to account for multi element fields, e.g. money field
        $('label[for^="' + this + '"]')
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
      this.setVisibility($(evt.target));
    },

    setVisibility: function($field) {
      var isShown = $field.val() === $field.data().conditionalShowValue + '';
      var id = $field.data().conditionalControls;

      if($field.is(':checkbox')) {
        isShown = isShown && $field.is(':checked');
      }

      $('[data-subfield-id="' + id +'"]')
        .toggleClass('s-expanded', isShown)
        .toggleClass('s-hidden', !isShown)
        .attr({
          'aria-expanded': isShown,
          'aria-hidden': !isShown
        });
    },

    cacheEls: function() {
      this.subfields = $(this.el);
    }
  };
}());
