'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var VERBOSE = true;
var RESULTS = {
  pass: 'result/eligible',
  fail: 'help-organisations/'
};

var SCENARIOS = []
  .concat(require('../modules/thresholds/single-person-capital'))
  .concat(require('../modules/thresholds/partner-capital'))
  .concat(require('../modules/thresholds/single-gross-income'))
  .concat(require('../modules/thresholds/joint-gross-income'))
  .concat(require('../modules/thresholds/over-4-children'))
  .concat(require('../modules/thresholds/cap-on-housing'))
  .concat(require('../modules/thresholds/employment-allowance'))
  .concat(require('../modules/thresholds/partner-allowance'))
  .concat(require('../modules/thresholds/own-expenses'))
  .concat(require('../modules/thresholds/partner-expenses'))
  .concat(require('../modules/thresholds/pensioner-disregard'))
  .concat(require('../modules/thresholds/multiple-properties'))
  .concat(require('../modules/thresholds/user-test-scenarios'))
  .concat(require('../modules/thresholds/calculator-timebase-scenarios'))
;

module.exports = {
  'Income threshold scenarios': function(client) {
    var setField = function(client, field, value) {
      client.getTagName(util.format('[name="%s"]', field), function(result) {
        if(result.value === 'select') {
          common.setDropdownValue(client, field, value, VERBOSE);
        } else if(result.value === 'input') {
          client.getAttribute(util.format('input[name="%s"]', field), 'type', function(result) {
            if(result.value === 'radio') {
              client.click(util.format('input[name="%s"][value="%s"]', field, value), function() {
                if(VERBOSE) {
                  console.log(util.format('Set %s to %s', field, (value === 1 ? 'yes' : 'no')));
                }
              });
            } else if(result.value === 'checkbox') {
              client.click(util.format('input[value="%s"]', value), function() {
                if(VERBOSE) {
                  console.log(util.format('Check %s', value));
                }
              });
            } else if(result.value === 'text') {
              client.setValue(util.format('input[name="%s"]', field), value, function() {
                if(VERBOSE) {
                  console.log(util.format('Set %s to %s', field, value));
                }
              });
            }
          });
        }
      });
    };

    // temp: just run last scenario
    // var s = SCENARIOS[SCENARIOS.length - 1];
    // SCENARIOS = [s];
    // /temp

    console.log(util.format('Running %s income threshold scenarios', SCENARIOS.length));

    SCENARIOS.forEach(function(scenario) {
      common.startPage(client, scenario.name);
      scenario.pages.forEach(function(page) {
        client
          .waitForElementVisible(util.format('form[action="/%s"]', page.page), 2000)
        ;
        if(page.page === 'property') {
          page.properties.forEach(function(property, i) {
            if(i > 0) {
              client.click('input[name="add-property"]');
            }
            client.waitForElementVisible(util.format('#property-set-%s', (i + 1) ), 2000, function() {
              for(var field in property) {
                if(property.hasOwnProperty(field)) {
                  setField(client, util.format('properties-%s-%s', i, field), property[field]);
                }
              }
            });
          });
        } else {
          for(var field in page.fields) {
            if(page.fields.hasOwnProperty(field)) {
              setField(client, field, page.fields[field]);
            }
          }
        }
        client.submitForm('form');
      });
      client.assert.urlContains(RESULTS[scenario.expected_result]);
    });

    client.end();
  }

};
