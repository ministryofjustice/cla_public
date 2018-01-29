'use strict';

moj.Modules.Progress = {
  progressStepLinks: [],

  init: function() {
    this.cacheEls();
    this.bindEvents();
  },

  bindEvents: function() {
    if(this.progressStepLinks.length === 0) {
      return;
    }

    this.progressStepLinks.focus(function(evt) {
      $(evt.target).parent().addClass('s-focused');
    });

    this.progressStepLinks.blur(function(evt) {
      $(evt.target).parent().removeClass('s-focused');
    });

    this.progressStepLinks.hover(function(evt) {
      $(evt.target).parent().addClass('s-hovered');
    }, function(evt) {
      $(evt.target).parent().removeClass('s-hovered');
    });
  },

  cacheEls: function() {
    this.progressStepLinks = $('.progress-step a');
  }
};
