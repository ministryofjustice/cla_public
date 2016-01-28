'use strict';

var util = require('util');
var common = require('../modules/common-functions');

exports.command = function(fields, value, callback) {
  var client = this;

  this.perform(function() {
    client.disableTransitions();

    function clickOption(field, value) {
      var el = util.format('input[name="%s"][value="%s"]', field, value);
      client
        .click(el, function() {
          console.log('     • Setting ‘' + field + '’' + ' to ‘' + common.humaniseValue(value) + '’');
        })
      ;
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
