'use strict';

var util = require('util');
var common = require('../../modules/common-functions');
var moment = require('moment');

var eligibleJourney = function(client) {
  common.startPage(client);

  common.selectDebtCategory(client);
  common.aboutPage(client);
  common.aboutPageSetAllToNo(client);
  common.setYesNoFields(client, 'on_benefits', 1);
  client
    .submitForm('form')
    .waitForElementVisible('input[name="benefits"]', 2000)
    .assert.urlContains('/benefits')
    .assert.containsText('h1', 'Your benefits')
    .assert.containsText('body', 'Are you on any of these benefits?')
    .click('input[value="income_support"]')
    .submitForm('form')
    .waitForElementVisible('input[name="callback_requested"]', 2000)
    .assert.urlContains('/result/eligible')
    .assert.containsText('h1', 'You might qualify for legal aid')
    .assert.containsText('h2', 'Contact Civil Legal Advice')
    .click('input[name="callback_requested"][value="1"]')
    .setValue('input[name="full_name"]', 'John Smith')
    .setValue('input[name="callback-contact_number"]', '01234 567890')
    .click('input[name="callback-safe_to_contact"][value="SAFE"]')
    .setValue('input[name="address-post_code"]', 'E18 1JA')
    .setValue('textarea[name="address-street_address"]', '3 Crescent Road\nLondon')
  ;
};

var checkCallbackTime = function(client, then, time) {
  then.hours(time.substr(0, 2));
  then.minutes(time.substr(2, 2));
  var formattedCallbackTime = then.format('dddd, D MMMM YYYY [at] HH:mm');

  client
    .submitForm('form')
    .waitForElementVisible('header.confirmation', 2000)
    .assert.containsText('h1', 'We will call you back')
    .verify.containsText('.main-content', formattedCallbackTime)
  ;
};

module.exports = {
  'Check callback today (next available)': function(client) {
    eligibleJourney(client);
    var timeIsMocked = process.argv.indexOf('-M') !== -1;
    var now = moment();
    if (timeIsMocked) {
      now = moment([2015, 0, 26, 9, 0]);
      console.log('MOCKING TIME TO 2015-1-26 9:00 - must be running ./manage.py mockserver');
    }
    if(now.day() !== 0) {
      if(now.hour() < 17) {
        if(now.day() === 6 && (now.hour() > 11 || (now.hour() === 11 && now.minute() > 14))) {
          console.log('Today not available after 11.15am on a Saturday, test skipped');
        } else {
          client.getValue('select[name="time_today"]', function(result) {
            checkCallbackTime(client, now, result.value);
          });
        }
      } else {
        console.log('Today not available after 7pm, test skipped');
      }
    } else {
      console.log('Today not available on Sunday, test skipped');
    }
  },

  'Check callback specific day': function(client) {
    eligibleJourney(client);

    client
      .click('input[name="specific_day"][value="specific_day"]')
      .click('select#id_day option:first-child')
      .click('body')
      .click('select#id_time_in_day option:first-child')
      .click('body')
      .getValue('select#id_day option:first-child', function(result) {
        var selectedDate = result.value;
        client.getValue('select#id_time_in_day option:first-child', function(result) {
          var then = moment([selectedDate.substr(0, 4), parseInt(selectedDate.substr(4, 2))-1, selectedDate.substr(6, 2)]);
          checkCallbackTime(client, then, result.value);
        });
      })
    ;

    client.end();
  }

};
