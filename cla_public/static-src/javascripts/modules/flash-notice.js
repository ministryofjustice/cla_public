(function () {
  'use strict';
  var _ = require('lodash');
  moj.Modules.FlashNotice = {
    $flashNotices: $(),

    init: function() {
      this.cacheEls();
      this.templates();
      this.bindEvents();
      this.addCloseButton();
    },

    cacheEls: function () {
      this.$flashNotices = $('.flash-messages');
    },

    bindEvents: function() {
      this.$flashNotices.on('click', '.flash-messages-close', function() {
        $(this).closest('.flash-messages').remove();
      });
    },

    addCloseButton: function() {
      var self = this;

      if(!self.$closeButton) {
        return;
      }

      $.each(this.$flashNotices, function() {
        $(this).append(self.$closeButton);
      });
    },

    templates: function () {
      var closeButton = _.template($('#flashMessageCloseButton').html());
      if(closeButton) {
        this.$closeButton = closeButton();
      }
    }
  };
}());
