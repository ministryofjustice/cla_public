 'use strict';
  var _ = require('lodash');
  var LOW_CHAR_COUNT = 80;

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
      var remainingCount = maxLength - value.length;

      function updateCount() {
        self.$currentCounter = $(self.characterCounter({
          count: remainingCount,
          counter_class: remainingCount < LOW_CHAR_COUNT ? 'counter-low' : ''
        }));

        return self.$currentCounter;
      }

      if(remainingCount < 0) {
        $textArea.val(value.slice(0, maxLength));
        return;
      }

      if(this.$currentCounter) {
        this.$currentCounter.replaceWith(updateCount());
      } else {
        $textArea.after(updateCount());
      }
    },

    removeCounter: function() {
      this.$currentCounter.remove();
      this.$currentCounter = null;
    },

    bindEvents: function() {
      this.textAreasWithCharCount
        .on('keyup', $.proxy(this.renderCounter, this))
        .focus($.proxy(this.renderCounter, this))
        .blur($.proxy(this.removeCounter, this));
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

