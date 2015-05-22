'use strict';

var util = require('util');
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

  'Scope diagnosis': function(client) {
    client.scopeDiagnosis('In scope', ['Debt', 'You own your own home', 'Yes']);
  },

  'About you': function(client) {
    client.aboutSetAllToNo(true, {
      'own_property': 1
    });
  },

  'Property page': function(client) {
    client
      .waitForElementVisible('input[name="properties-0-is_main_home"]', 5000)
      .assert.urlContains('/property')
      .assert.containsText('h1', 'Your property')
    ;
  },

  'Test currency formatting': function(client) {
    var checkValue = function(strIn, strOut) {
      var field = 'input[name="properties-0-property_value"]';
      client
        .clearValue(field)
        .click(field)
        .setValue(field, [strIn, client.Keys.TAB])
        .click('body')
        .pause(200)
        .assert.value(field, strOut, util.format('Check that currency value of %s is coverted to %s', strIn, strOut))
      ;
    };

    CURRENCY_CHECKS.forEach(function(values) {
      checkValue(values[0], values[1]);
    });

    client.end();
  }
};
