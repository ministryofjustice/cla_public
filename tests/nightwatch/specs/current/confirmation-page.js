'use strict';

var moment = require('moment');

var eligibleJourney = function(client) {
  client
    .startService()
    .selectCategory('debt', true)
    .aboutSetAllToNo(true, {
      'on_benefits': 1
    })
    .selectBenefit('income_support', true)
    .confirmReviewPage()
    .fillInContactDetails(false, {
      callback_requested: 1,
      'callback-safe_to_contact': 'SAFE'
    })
  ;
};

var checkFlashMessage = function(client) {
  client
    .assert.elementPresent('.flash-messages',
      'Has flash message informing about clearing the session')
    // Refresh page
    .url(function(result) { this.url(result.value); })
    .assert.elementNotPresent('.flash-messages',
      'Flash message is gone after refresh')
  ;
};

var checkCallbackTime = function(client, then, time) {
  then.hours(time.substr(0, 2));
  then.minutes(time.substr(2, 2));
  var formattedCallbackTime = then.format('dddd, D MMMM YYYY [at] HH:mm');

  client
    .submitForm('form')
    .waitForElementVisible('header.confirmation', 5000)
    .assert.containsText('h1', 'We will call you back')
    .verify.containsText('.main-content', formattedCallbackTime)
  ;

  checkFlashMessage(client);
};

module.exports = {
  'Check callback today (next available)': function(client) {
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
          eligibleJourney(client);
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
  }
};
