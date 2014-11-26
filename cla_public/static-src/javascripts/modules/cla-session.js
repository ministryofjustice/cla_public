(function () {
  'use strict';

  moj.Modules.CLASession = {
    validNavigation: false,

    init: function() {
      this.keepSessionAlive();
    },

    keepSessionAlive: function () {
      setInterval(function () {
        $.get('/session_keep_alive');
      }, 30000);
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
}());
