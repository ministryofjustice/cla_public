 'use strict';
  var _ = require('lodash');
  var LOW_CHAR_COUNT = 80;

  if (GOVUK.getCookie("locale") == "cy_GB") {
    var youHave = '';
    var someCharactersRemaining = 'nodau ar ôl';
    var oneCharacterRemaining = 'nod ar ôl';
    var oneCharacterTooMany = 'nod gormod';
    var someCharactersTooMany = 'nodau gormod';
  } else {
    var youHave = 'You have';
    var someCharactersRemaining = 'characters remaining';
    var oneCharacterRemaining = 'character remaining';
    var oneCharacterTooMany = 'character too many';
    var someCharactersTooMany = 'characters too many';
  }

  moj.Modules.TextAreaCharacterCount = {
    $currentCounter: null,

    init: function() {
      this.cacheEls();

      if(this.textAreasWithCharCount.length) {
        this.templates();
        this.bindEvents();
      }
    },

    renderCounter: function(evt) {
      var self = this;
      var $textArea = $(evt.target);
      var value = $textArea.val();
      var maxLength = $textArea.data('character-count');
      var numberOfLineReturns = (value.match(/\n/g) || []).length;
      var remainingCount = maxLength - value.length - numberOfLineReturns;
      if (remainingCount < -1) {
        var remainText = someCharactersTooMany;
      } else if (remainingCount === -1) {
        var remainText = oneCharacterTooMany;
      } else if (remainingCount === 1) {
        var remainText = oneCharacterRemaining;
      } else { // > 1 or 0
        var remainText = someCharactersRemaining;
      }

      function updateCount() {
        self.$currentCounter = $(self.characterCounter({
          count: remainingCount < 0 ? remainingCount*-1 : remainingCount,
          counter_class: remainingCount < 0 ? 'govuk-error-message' : 'govuk-hint',
          you_have: youHave,
          remaining_text: remainText
        }));

        $textArea.removeClass("govuk-textarea--error")
        if (remainingCount < 0) $textArea.addClass("govuk-textarea--error");

        return self.$currentCounter;
      }

      if(this.$currentCounter) {
        this.$currentCounter.replaceWith(updateCount());
      } else {
        $textArea.after(updateCount());
      }
    },

    bindEvents: function() {
      this.textAreasWithCharCount
        .on('keyup', $.proxy(this.renderCounter, this))
        .focus($.proxy(this.renderCounter, this));
    },

    cacheEls: function() {
      this.textAreasWithCharCount = $('textarea[data-character-count]')
        .filter(function() {
          return typeof $(this).data('character-count') === 'number';
        });
    },

    templates: function() {
      this.characterCounter = _.template($('#characterCounter').html());
    }
  };

