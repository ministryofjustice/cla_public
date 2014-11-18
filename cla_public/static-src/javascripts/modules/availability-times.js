(function () {
  'use strict';

  var on_saturday = function (time) {
    return time.getDay() === 6;
  };

  var is_today = function (time) {
    var today = new Date();
    return time.getFullYear() === today.getFullYear() &&
      time.getMonth() === today.getMonth() &&
      time.getDate() === today.getDate();
  };

  var too_late = function (time) {
    var cut_off = new Date();
    cut_off.setHours(cut_off.getHours() + 1);
    return time <= cut_off;
  };

  var after_1230 = function (time) {
    var twelve_thirty = new Date(time);
    twelve_thirty.setHours(12, 30, 0, 0);
    return time >= twelve_thirty;
  };

  var available = function (time) {

    if (on_saturday(time) && after_1230(time)) {
      return false;
    }

    if (is_today(time) && too_late(time)) {
      return false;
    }

    return true;
  };

  var setEnabled = function (option, enabled) {
    option.disabled = !enabled;
    $(option).toggle(enabled);
  };

  moj.Modules.AvailabilityTimes = {
    el: '#id_day',

    init: function () {
      _.bindAll(this, 'render');
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function () {
      function check(el) {
        return function () {
          el.prop('checked', true);
        };
      }

      this.$day_select
        .on('change', this.render)
        .on('focus', check(this.$specific_day));

      this.$time_select
        .on('focus', check(this.$specific_day));

      this.$today_time_select
        .on('focus', check(this.$today));

      this.$tomorrow_time_select
        .on('focus', check(this.$tomorrow));

      moj.Events.on('render AvailabilityTimes.render', this.render);
    },

    cacheEls: function () {
      this.$day_select = $(this.el);
      this.$time_select = $('[name=time_in_day]');
      this.$today_time_select = $('[name=time_today]');
      this.$tomorrow_time_select = $('[name=time_tomorrow]');
      this.$today = $('[name=specific_day][value=today]');
      this.$tomorrow = $('[name=specific_day][value=tomorrow]');
      this.$specific_day = $('[name=specific_day][value=specific_day]');
    },

    slot: function (time) {
      var date = this.$day_select.val();
      time = time || this.$time_select.val();
      var year = date.slice(0, 4);
      var month = parseInt(date.slice(4, 6)) - 1;  // JS months start at 0
      var day = date.slice(6);
      var hour = time.slice(0, 2);
      var minute = time.slice(2);
      return new Date(year, month, day, hour, minute);
    },

    render: function () {
      var self = this;

      $.each(this.$time_select.children(), function () {
        setEnabled(this, available(self.slot($(this).val())));
      });

      this.$time_select.children(':not(:disabled)').first().attr('selected', true);
    }
  };
}());
