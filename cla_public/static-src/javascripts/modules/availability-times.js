 'use strict';
  var _ = require('lodash');
  moj.Modules.AvailabilityTimes = {
    el: '[data-day-time-choices]',

    init: function() {
      if($(this.el).length === 0) {
        return;
      }
      _.bindAll(this, 'handleDayChange');
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function() {
      this.$daySelectors.on('change', this.handleDayChange);
      this.$timeSelectors.on('change', this.handleTimeRadioCheck);
      this.$todayTimeSelectors.on('change', this.handleTimeRadioCheck);
    },

    cacheEls: function() {
      this.$daySelectors = $(this.el);
      this.$timeSelectors = $('[name$=time_in_day]');
      this.$todayTimeSelectors = $('[name$=time_today]');
    },

    handleTimeRadioCheck: function(evt) {
      var $target = $(evt.target);
      var $radioButton = $target.closest('li').find('[type=radio]');

      var targetName = $target.attr('name');
      if(window.ga && targetName) {
        window.ga('send', 'event', 'availability-times', 'select', targetName);
      }
      $radioButton
        .prop('checked', true)
        .trigger('label-select');
    },

    handleDayChange: function(evt) {
      this.handleTimeRadioCheck(evt);
    }
  };

