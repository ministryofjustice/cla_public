 'use strict';
  var numeral = require('numeral')
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
      // Disable selects for 0s and non-numbers
      this.currencyFields.on('keyup', this.handleFrequencySelect);
    },

    formatCurrency: function(evt) {
      var $field = $(evt.target);
      var entry = $field.val().toString().replace(/,/g, '');

      if(!isNaN(parseFloat(entry))) {
        $field.val(numeral(entry).format('0,0.00'));
      }
    },

    handleFrequencySelect: function(evt) {
      var $field = $(evt.target);
      var value = _.trim($field.val());
      var valueNumber = parseInt(value, 10);

      if (value &&
        (_.isNaN(valueNumber) || _.isNumber(valueNumber) && valueNumber / 1 === 0)
      ) {
        $field.siblings('select').attr('disabled', true);
      } else {
        $field.siblings('select').attr('disabled', false);
      }
    },

    cacheEls: function() {
      this.currencyFields = $('.input-prefix:contains("£") + input');
    }
  };

