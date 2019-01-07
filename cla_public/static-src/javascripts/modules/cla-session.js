 'use strict';

  moj.Modules.CLASession = {
    validNavigation: false,

    init: function() {
      this.bindEvents();
      this.keepSessionAlive();
    },

    bindEvents: function() {
      $(window).on('unload',  $.proxy(this.clearSessionIfNotValid, this));

      $('a').on('click',  $.proxy(this.isValidNavigation, this));

      $('button').on('click',  $.proxy(this.isValidNavigation, this));

      $('form').on('submit',  $.proxy(this.isValidNavigation, this));
    },

    keepSessionAlive: function () {
      $.get('/session_keep_alive');
      var self = this;
      setTimeout(function () {
        self.keepSessionAlive();
      }, 10000);
    },

    isValidNavigation: function () {
      this.validNavigation = true;
    },

    clearSessionIfNotValid: function () {
      if (!this.validNavigation) {
        this.clearSession();
      }
    },

    clearSession: function () {
      $.ajax({
        url: '/session_end',
        async: false
      });
    }
  };

