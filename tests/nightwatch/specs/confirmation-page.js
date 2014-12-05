'use strict';

var util = require('util');
var common = require('../modules/common-functions');

var eligibleJourney = function(client) {
  common.startPage(client);

  common.selectDebtCategory(client);
  client
    .assert.urlContains('/about')
    .assert.containsText('h1', 'About you')
  ;
  common.aboutPageSetAllToNo(client);
  common.setYesNoFields(client, 'on_benefits', 1);
  client.submitForm('form');
  client
    .assert.urlContains('/benefits')
    .assert.containsText('h1', 'Your benefits')
    .assert.containsText('body', 'Are you on any of these benefits?')
    .click('input[value="income_support"]')
    .submitForm('form')
  ;
  client
    .assert.urlContains('/result/eligible')
    .assert.containsText('h1', 'You might qualify for legal aid')
    .assert.containsText('h2', 'Request a callback')
    .setValue('input[name="full_name"]', 'John Smith')
    .setValue('input[name="contact_number"]', '01234 567890')
    .setValue('input[name="contact_number"]', '01234 567890')
    .click('input[name="safe_to_contact"][value="SAFE"]')
    .setValue('input[name="post_code"]', 'E18 1JA')
    .setValue('textarea[name="address"]', '3 Crescent Road\nLondon')
  ;
  client.getValue('select[name="time_today"]', function(result) {
    console.log(result.value);
  });
};

module.exports = {
  'Eligible journey': eligibleJourney,

  'Check callback today (next available)': function(client) {
    var now = new Date();
    if(now.getDay() !== 0) {
      // TODO: latest callback on a saturday is 1215
      if(now.getHours() < 19) {
        client.getValue('select[name="time_today"]', function(result) {
          // TODO: write checkCallbackTime function :)
          checkCallbackTime(client, now.getDay(), result.value);
        });
      } else {
        console.log('Today not available after 7pm, test skipped');
      }
    } else {
      console.log('Today not available on Sunday, test skipped');
    }
  },

  'end': function(client) {
    client.end();
  }

};
