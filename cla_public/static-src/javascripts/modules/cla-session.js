 'use strict';

  moj.Modules.CLASession = {
    validNavigation: false,
    // 30 minutes
    inactiveMilliseconds: 1800000,

    init: function() {
    var self = this;
      this.bindEvents();
      this.keepSessionAlive();
      this.monitorSessionActivity();
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

    monitorSessionActivity: function() {
      var self = this;
      var activityTimer = setTimeout(self.clearSession, self.inactiveMilliseconds);
      $(document).bind('keypress scroll', function(){
        clearTimeout(activityTimer);
        activityTimer = setTimeout(self.clearSession, self.inactiveMilliseconds);
      });
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

