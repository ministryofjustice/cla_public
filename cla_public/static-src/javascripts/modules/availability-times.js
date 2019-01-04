(function () {
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

    _populateDayTime: function($daySelector) {
      var dayTimeHours = $daySelector.data('day-time-choices');
      var dayValue = $daySelector.val();

      if(!dayValue || !dayTimeHours) {
        return;
      }

      var dayTimes = dayTimeHours[dayValue];
      var timeOptions = _.keys(dayTimes).sort();
      var $timeSelector = $daySelector.closest('[role=radiogroup]').find(this.$timeSelectors);
      var $options = _.map(timeOptions, function(v) {
        var d = dayTimes[v];
        return $('<option>', { value: v, html: d });
      });

      $timeSelector
        .html($options)
        .val(timeOptions[Math.floor(Math.random() * timeOptions.length)]);
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
      this._populateDayTime($(evt.target));
      this.handleTimeRadioCheck(evt);
    }
  };
}());
