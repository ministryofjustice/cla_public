(function () {
  'use strict';

  var onSaturday = function (time) {
    return time.getDay() === 6;
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
          if(window.ga) {
            window.ga('send', 'event', 'availability-times', 'select', this.name);
          }
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
      var availableTimes = [];

      $.each(this.$timeSelect.children(), function () {
        var isAvailable = available(self.slot($(this).val()));
        setEnabled(this, isAvailable);
        if (isAvailable) {
          availableTimes.push($(this).val());
        } else if ($(this).prop('selected')) {
          self.$timeSelect.val(
            availableTimes[Math.floor(Math.random()*availableTimes.length)]
          );
        }
      });

    }
  };
}());
