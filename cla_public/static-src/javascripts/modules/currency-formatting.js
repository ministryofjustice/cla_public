(function () {
  'use strict';

  moj.Modules.CurrencyFormatting = {
    currencyFields: [],

    init: function() {
      this.cacheEls();
      this.bindEvents();
      this.currencyFields.each(function(){
        $(this).trigger('blur');
      });
    },

    bindEvents: function() {
      this.currencyFields.on('blur', this.formatCurrency);
    },

    formatCurrency: function(evt) {
      var $field = $(evt.target);
      var entry = $field.val().toString().replace(/,/g, '');

      if(!isNaN(parseFloat(entry))) {
        $field.val(numeral(entry).format('0,0.00'));
      }
    },

    cacheEls: function() {
      this.currencyFields = $('.input-prefix:contains("£") + input');
    }
  };
}());
