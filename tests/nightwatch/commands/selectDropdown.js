'use strict';

// setValue on <select> items doesn’t work in Firefox

var util = require('util');

exports.command = function(fieldName, value) {
  var client = this;

  this.perform(function() {
    client
      .click(util.format('select[name="%s"]', fieldName))
      .click(util.format('select[name="%s"] option[value="%s"]', fieldName, value))
      .setValue(util.format('select[name="%s"]', fieldName), client.Keys.ENTER, function () {
        console.log('     • Setting dropdown ‘' + fieldName + '’' + ' to ‘' + value + '’');
      })
    ;
  });

  return client;
};
