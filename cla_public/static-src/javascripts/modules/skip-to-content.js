'use strict';

var _ = require('lodash');

moj.Modules.SkipToContent = {
  init: function() {
    this.bindEvents();
  },

  bindEvents: function() {
    $('.skiplink').on('click', function(evt) {
      evt.preventDefault();
      var href = $(evt.target).attr('href');
      $(href).attr('tabindex', -1).focus();
    });

    $('#content').on('blur', function() {
      $(this).removeAttr('tabindex');
    });
  }
};
