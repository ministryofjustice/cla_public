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
          var $fields = $('[name="' + $(this).data('controlled-by') + '"]');

          $fields = $fields.filter(function() {
            // Unchecked checkbox or checked radio button
            return this.type === 'checkbox' || $(this).is(':checked');
          });

          $fields.each($.proxy(self.handleVisibility, self));
        });
    },

    // If CONDITIONAL_LABELS constant exists its contents will be used to
    // replace fields on page load.

    // e.g. If non-JS page has a label "If Yes, how many?" (referring to previous field)
    // Adding `CONDITIONAL_LABELS['num_children'] = 'How many?'` would change label to 'How many?'
    // when JS kicks in.
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
        return $(this).data('controlled-by');
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
      // `controlled-by` specifies the field name which controls the visibility of element
      var controlInputName = $field.data('controlled-by');
      // `control-value` is the value which should trigger the visibility of element
      var controlInputValue = $field.data('control-value') + '';
      var $controlInput = $('[name="' + controlInputName + '"]');

      // control visibility only for specified value (unless it's a wildcard `*`)
      if(controlInputValue && controlInputValue !== '*') {
        $controlInput = $controlInput.filter('[value="' + controlInputValue + '"]');
      }

      this._toggleField($field, $controlInput);
    },

    _toggleField: function($field, $controlInput) {
      var isVisible = $controlInput.is(':checked');
      $field
        .toggleClass('s-expanded', isVisible)
        .toggleClass('s-hidden', !isVisible)
        .attr('aria-hidden', !isVisible);
      $controlInput.attr('aria-expanded', isVisible);

      if(!isVisible && !$field.data('persist-values')) {
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
