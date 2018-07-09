'use strict';

var util = require('util');
var constants = require('../modules/constants');

var CURRENCY_CHECKS = [
  ['1', '1.00'],
  ['00001', '1.00'],
  ['12', '12.00'],
  ['123', '123.00'],
  ['1234', '1,234.00'],
  ['12345', '12,345.00'],
  ['123456', '123,456.00'],
  ['1234567', '1,234,567.00'],
  ['.89', '0.89'],
  ['.1', '0.10'],
  ['.01', '0.01'],
  ['456789.0', '456,789.00'],
  ['456789.00', '456,789.00'],
  ['1234.5', '1,234.50'],
  ['1234.56', '1,234.56'],
  ['1234567.8', '1,234,567.80'],
  ['1234567.89', '1,234,567.89']
];

module.exports = {
  'Start page': function(client) {
    client.startService();
  },

  '@disabled': true,
  'Scope diagnosis': function(client) {
    client.scopeDiagnosis(constants.SCOPE_PATHS.debtInScope);
  },

  'Interstitial page': function(client) {
    client.interstitialPage();
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true, {
      'own_property': 1
    });
  },

  'Property page': function(client) {
    client.ensureCorrectPage('#properties-0-is_main_home-0', '/property', {
      'h1': 'Your property'
    });
  },

  'Test currency formatting': function(client) {
    var checkValue = function(strIn, strOut) {
      var field = 'input[name="properties-0-property_value"]';
      client
        .clearValue(field)
        .click(field)
        .setValue(field, [strIn, client.Keys.TAB])
        .assert.value(field, strOut,
          util.format('  - Currency value of %s is converted to %s', strIn, strOut)
        )
      ;
    };

    CURRENCY_CHECKS.forEach(function(values) {
      checkValue(values[0], values[1]);
    });

    client.end();
  }
};
