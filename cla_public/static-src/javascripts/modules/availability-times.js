(function () {
  'use strict';

  var onSaturday = function (time) {
    return time.getDay() === 6;
  };

  var isToday = function (time) {
    var today = new Date();
    return time.getFullYear() === today.getFullYear() &&
      time.getMonth() === today.getMonth() &&
      time.getDate() === today.getDate();
  };

  var tooLate = function (time) {
    var cutOff = new Date();
    cutOff.setHours(cutOff.getHours() + 1);
    return time <= cutOff;
  };

  var after1230 = function (time) {
    var twelveThirty = new Date(time);
    twelveThirty.setHours(12, 30, 0, 0);
    return time >= twelveThirty;
  };

  var available = function (time) {

    if (onSaturday(time) && after1230(time)) {
      return false;
    }

    if (isToday(time) && tooLate(time)) {
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
          el
            .prop('checked', true)
            .trigger('label-select');
        };
      }

      this.$daySelect
        .on('change', this.render)
        .on('change', check(this.$specificDay));

      this.$timeSelect
        .on('change', check(this.$specificDay));

      this.$todayTimeSelect
        .on('change', check(this.$today));

      moj.Events.on('render AvailabilityTimes.render', this.render);
    },

    cacheEls: function () {
      this.$daySelect = $(this.el);
      this.$timeSelect = $('[name=time_in_day]');
      this.$todayTimeSelect = $('[name=time_today]');
      this.$today = $('[name=specific_day][value=today]');
      this.$specificDay = $('[name=specific_day][value=specific_day]');
    },

    slot: function (time) {
      var date = this.$daySelect.val();
      time = time || this.$timeSelect.val();
      var year = date.slice(0, 4);
      var month = parseInt(date.slice(4, 6)) - 1;  // JS months start at 0
      var day = date.slice(6);
      var hour = time.slice(0, 2);
      var minute = time.slice(2);
      return new Date(year, month, day, hour, minute);
    },

    render: function () {
      var self = this;

      $.each(this.$timeSelect.children(), function () {
        setEnabled(this, available(self.slot($(this).val())));
      });

      this.$timeSelect.children(':not(:disabled)').first().attr('selected', true);
    }
  };
}());
