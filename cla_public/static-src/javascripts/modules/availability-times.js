(function () {
  'use strict';

  moj.Modules.AvailabilityTimes = {
    el: '#id_day',

    init: function () {
      _.bindAll(this, 'render');
      this.cacheEls();
      this.cacheData();
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

    cacheData: function () {
      this.dayTimeHours = this.$daySelect.data('day-time-choices');
    },

    render: function () {
      var self = this;

      if (this.$daySelect.val()) {
        var dayTimes = this.dayTimeHours[this.$daySelect.val()];
        var timeOptions = _.keys(dayTimes).sort();

        this.$timeSelect.html('');
        $.each(timeOptions, function(i, v){
          var d = dayTimes[v];
          self.$timeSelect.append($('<option>', {value: v, html: d}));
        });
        this.$timeSelect.val(
          timeOptions[Math.floor(Math.random()*timeOptions.length)]
        );
      }
    }
  };
}());
