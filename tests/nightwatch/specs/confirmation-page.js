'use strict';

var util = require('util');
var common = require('../modules/common-functions');
var moment = require('moment');

var eligibleJourney = function(client) {
  common.startPage(client);

  common.selectDebtCategory(client);
  common.aboutPage(client);
  common.aboutPageSetAllToNo(client);
  common.setYesNoFields(client, 'on_benefits', 1);
  client
    .submitForm('form')
    .waitForElementVisible('form[action="/benefits"]', 2000)
    .assert.urlContains('/benefits')
    .assert.containsText('h1', 'Your benefits')
    .assert.containsText('body', 'Are you on any of these benefits?')
    .click('input[value="income_support"]')
    .submitForm('form')
    .waitForElementVisible('form[action="/result/eligible"]', 2000)
    .assert.urlContains('/result/eligible')
    .assert.containsText('h1', 'You might qualify for legal aid')
    .assert.containsText('h2', 'Request a callback')
    .setValue('input[name="full_name"]', 'John Smith')
    .setValue('input[name="contact_number"]', '01234 567890')
    .click('input[name="safe_to_contact"][value="SAFE"]')
    .setValue('input[name="post_code"]', 'E18 1JA')
    .setValue('textarea[name="address"]', '3 Crescent Road\nLondon')
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

    var now = moment();
    if(now.day() !== 0) {
      if(now.hour() < 19) {
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

  'Check callback tomorrow': function(client) {
    eligibleJourney(client);

    var now = moment();
    if(now.day() !== 6) {
      client
        .click('input[name="specific_day"][value="tomorrow"]')
        .getValue('select[name="time_tomorrow"]', function(result) {
        checkCallbackTime(client, now.add(1, 'days'), result.value);
      });
    } else {
      console.log('Tomorrow not available on Saturday, test skipped');
    }
  },

  'Check callback specific day': function(client) {
    eligibleJourney(client);

    client
      .click('input[name="specific_day"][value="specific_day"]')
      .click('select#id_day')
      .click('select#id_day option:last-child')
      .click('select#id_time_in_day')
      .click('select#id_time_in_day option:last-child')
      .click('body')
      .getValue('select#id_day option:last-child', function(result) {
        var selectedDate = result.value;
        client.getValue('select#id_time_in_day option:last-child', function(result) {
          var then = moment([selectedDate.substr(0, 4), parseInt(selectedDate.substr(4, 2))-1, selectedDate.substr(6, 2)]);
          checkCallbackTime(client, then, result.value);
        });
      })
    ;
  },

  'end': function(client) {
    client.end();
  }

};
