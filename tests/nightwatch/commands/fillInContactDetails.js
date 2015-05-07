'use strict';

var _ = require('lodash');
var log = require('../modules/log');
var common = require('../modules/common-functions');

exports.command = function(shouldSubmitForm, options, callback) {
  var client = this;

  options = options || {
    callback_requested: 0
  };

  this.perform(function() {
    log.command('Processing Contact page…');

    client
      .waitForElementVisible('.contact-form', 3000,
        '  - Contact form exists')
      .setValue('#full_name', 'John Smith', function() {
        console.log('     • Set name to John Smith');
      })
      .setValue('input[name="address-post_code"]', 'E18 1JA', function() {
        console.log('     • Set postcode to E18 1JA');
      })
      .setValue('textarea[name="address-street_address"]', '3 Crescent Road\nLondon', function() {
        console.log('     • Set address to: 3 Crescent Road, London');
      })
    ;

    if(options instanceof Object) {
      _.each(options, function(value, name) {
        // Pause to ensure reveal animations are completed
        if(common.humaniseValue(value) === 'Yes') {
          client.pause(500);
        }
        client.setYesNoFields(name, value, function() {
          console.log('     • Option `' + name + '` set to ‘' + common.humaniseValue(value) + '’');
        });
      });
    }

    client.isVisible('input[name="callback-contact_number"]', function() {
      this.setValue('input[name="callback-contact_number"]', '01234 567890', function(result) {
        if(!result.error) {
          console.log('     • Set callback number to 01234 567890');
        }
      });
    });

    client.conditionalFormSubmit(shouldSubmitForm);
  });

  if (typeof callback === 'function') {
    callback.call(client);
  }

  return client;
};
