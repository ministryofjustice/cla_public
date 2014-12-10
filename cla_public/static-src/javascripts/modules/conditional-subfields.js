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
          .first()
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
      var isShown = $field.val() ? $field.val() === $field.data().conditionalShowValue + '': true;
      var conditionalControls = $field.data().conditionalControls;
      var ids = [];
      if (conditionalControls) {
        ids = $.isArray(conditionalControls) ? conditionalControls : [conditionalControls];
      }

      if($field.is(':checkbox')) {
        isShown = isShown && $field.is(':checked');
      }

      $.each(ids, function(index, id) {
        var $conditionalContainer = $('[data-subfield-id="' + id +'"]');
        $conditionalContainer
          .toggleClass('s-expanded', isShown)
          .toggleClass('s-hidden', !isShown)
          .attr({
            'aria-expanded': isShown,
            'aria-hidden': !isShown
          });

        if (!isShown) {
          $('input[type="radio"]', $conditionalContainer)
            .prop('checked', false)
            .first()
            .change();
        }
      });
    },

    cacheEls: function() {
      this.subfields = $(this.el);
    }
  };
}());
