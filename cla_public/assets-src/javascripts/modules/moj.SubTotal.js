(function () {
  'use strict';

  moj.Modules.SubTotal = {
    el: '.js-SubTotal',

    init: function () {
      _.bindAll(this, 'render', 'showSummary', 'calculate');
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function () {
      this.$sets.on('keyup', 'input[type=number]', this.showSummary);

      moj.Events.on('render', this.render);
    },

    cacheEls: function () {
      this.$sets = $(this.el);
    },

    render: function () {
      this.$sets.each(this.showSummary);
    },

    calculate: function (set) {
      var total = 0;

      set.find('input[type=number]').each(function (i, el) {
        var val = parseFloat($(el).val());
        if (!isNaN(val)) {
          total += val;
        }
      });

      return total;
    },

    showSummary: function (e, el) {
      var $set = el !== undefined ? $(el) : $(e.target).closest(this.el),
          value = this.calculate($set);

      moj.log(CLA.templates);

      if ($set.find('.SubTotal').length > 0) {
        $set.find('.SubTotal').replaceWith(CLA.templates.SubTotal({value: value}));
      } else {
        $set.append(CLA.templates.SubTotal({value: value}));
      }
    }
  };
}());