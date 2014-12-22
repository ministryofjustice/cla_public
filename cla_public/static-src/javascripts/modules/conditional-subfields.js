(function () {
  'use strict';

  moj.Modules.ConditionalSubfields = {
    el: '[data-controlled-by]',

    init: function() {
      this.cacheEls();
      this.bindEvents();
      this.setInitialState();
      this.replaceLabels();
    },

    setInitialState: function() {
      var self = this;

      this.conditionalFields
        .each(function() {
          var $fields = $('[name="' + $(this).data().controlledBy + '"]');
          $fields = $fields.filter(function() {
            // Unchecked checkbox or checked radio button
            return this.type === 'checkbox' || $(this).is(':checked');
          });

          $fields.each($.proxy(self.handleVisibility, self));
        });
    },

    replaceLabels: function() {
      if(!window.CONDITIONAL_LABELS) {
        return;
      }

      $.each(window.CONDITIONAL_LABELS, function(key, value) {
        $('#field-' + key + '')
          .find('.fieldset-label *')
          .text(value);
      });
    },

    bindEvents: function() {
      var self = this;

      var controllers = $.unique(this.conditionalFields.map(function() {
        return $(this).data().controlledBy;
      }));

      $.each(controllers, function() {
        $('[name="' + this + '"]').on('change', $.proxy(self.handleVisibility, self));
      });
    },

    handleVisibility: function() {
      var self = this;

      this.conditionalFields.each(function() {
        self._handleField($(this));
      });
    },

    _handleField: function($field) {
      var controlInputName = $field.data().controlledBy;
      var controlInputValue = $field.data().controlValue + '';
      var $controlInput = $('[name="' + controlInputName + '"][value="' + controlInputValue + '"]');

      this._toggleField($field, $controlInput.is(':checked'));
    },

    _toggleField: function($field, isVisible) {
      $field
        .toggleClass('s-expanded', isVisible)
        .toggleClass('s-hidden', !isVisible)
        .attr({
          'aria-expanded': isVisible,
          'aria-hidden': !isVisible
        });

      if(!isVisible) {
        $field.find('input')
          .prop('checked', false)
          .trigger('label-select');
      }
    },

    cacheEls: function() {
      this.conditionalFields = $(this.el);
    }
  };
}());
