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
        .each(function(i, item) {
          var $fields = $('[name="' + $(this).data().controlledBy + '"]');
          $fields = $fields.filter(function() {
            // Unchecked checkbox or checked radio button
            return this.type === 'checkbox' || $(this).is(':checked');
          });

          $fields.each(function() {
            self.setVisibility($(this), $(item));
          });
        });
    },

    replaceLabels: function() {
      if(!window.CONDITIONAL_LABELS) {
        return;
      }

      // Find labels defined in template and replace the text.
      // Exclude the prefix/suffix labels
      $.each(window.CONDITIONAL_LABELS, function(key, value) {
        // Use 'begins with' to account for multi element fields, e.g. money field
        $('#field-' + key + '')
          .find('.fieldset-label *')
          .text(value);
      });
    },

    bindEvents: function() {
      var self = this;

      $.each(this.conditionalFields, function(i, item) {
        var controllerId = $(item).data().controlledBy;

        $('[name="' + controllerId + '"]')
          .on('change', function(evt) {
            self.handleChange(evt, item);
          });
      });
    },

    handleChange: function(evt, item) {
      this.setVisibility($(evt.target), $(item));
    },

    setVisibility: function($controllerField, $controlledField) {
      var isShown = $controllerField.val() ? $controllerField.val() === $controlledField.data().controlValue + '' : true;

      if($controllerField.is(':checkbox')) {
        isShown = isShown && $controllerField.is(':checked');
      }

      $controlledField
        .toggleClass('s-expanded', isShown)
        .toggleClass('s-hidden', !isShown)
        .attr({
          'aria-expanded': isShown,
          'aria-hidden': !isShown
        });
    },

    cacheEls: function() {
      this.conditionalFields = $(this.el);
    }
  };
}());
