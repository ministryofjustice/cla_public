'use strict';

var _ = require('lodash');
var ABOUT_YOU_QUESTIONS = require('../modules/constants').ABOUT_YOU_QUESTIONS;
var log = require('../modules/log');
var common = require('../modules/common-functions');

exports.command = function(shouldSubmitForm, options, callback) {
  var client = this;
  options = options || {};

  this.perform(function() {
    log.command('Processing About you page…');

    client
      .assert.urlContains('/about',
        '  - About you page URL is correct')
      .setYesNoFields(ABOUT_YOU_QUESTIONS, 0, function() {
        console.log('     • All values set to ‘No’');
      })
    ;

    if(options instanceof Object) {
      _.each(options, function(value, name) {
        client.setYesNoFields(name, value, function() {
          console.log('       • Additionally, `' + name + '` set to ‘' + common.humaniseValue(value) + '’');
        });
      });
    }

    client.conditionalFormSubmit(shouldSubmitForm);
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
