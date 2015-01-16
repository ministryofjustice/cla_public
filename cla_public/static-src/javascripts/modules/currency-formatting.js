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
        var pence = Math.round(parseFloat(entry)*100);
        var pennies = pence % 100;
        var pounds = Math.floor(pence/100);

        $field.val(pounds.toLocaleString() + '.' + (pennies < 10 ? '0' : '') + pennies.toString());
      }
    },

    cacheEls: function() {
      this.currencyFields = $('.input-prefix:contains("£") + input');
    }
  };
}());
