'use strict';

var util = require('util');
var common = require('../modules/common-functions');

exports.command = function(fields, value, callback) {
  var client = this;

  this.perform(function() {
    var attemptedOnce = false;

    function clickOption(field, value) {
      var el = util.format('input[name="%s"][value="%s"]', field, value);
      client.isVisible(el, function(result) {
        if(result.value === true) {
          client.click(el, function() {
            console.log('     • Setting ‘' + field + '’' + ' to ‘' + common.humaniseValue(value) + '’');
          });
        // Take into account transitions if element happens to be invisible straight away
        } else if(!attemptedOnce) {
          client.pause(200, function() {
            clickOption(field, value);
            attemptedOnce = true;
          });
        }
      });
    }

    if(fields.constructor === Array) {
      fields.forEach(function(field) {
        clickOption(field, value);
      });
    } else {
      clickOption(fields, value);
    }
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
