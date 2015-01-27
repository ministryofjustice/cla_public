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
        var pounds = Math.floor(pence/100).toString();
        var formattedPounds = pounds;
        if(pounds.length > 3) {
          var reversePounds = pounds.split('').reverse().join('');
          formattedPounds = [];
          for(var x = 0; x < reversePounds.length; x++) {
            if(x > 1 && (x % 3) === 0) {
              formattedPounds.push(',');
            }
            formattedPounds.push(reversePounds[x]);
          }
          formattedPounds = formattedPounds.reverse().join('');
        }

        $field.val(formattedPounds + '.' + (pennies < 10 ? '0' : '') + pennies.toString());
      }
    },

    cacheEls: function() {
      this.currencyFields = $('.input-prefix:contains("£") + input');
    }
  };
}());
