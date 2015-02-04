(function () {
  'use strict';

  // To send custom events:
  // <a href="/link" data-ga="event:category/action/label">Link</a>
  // To send custom page view:
  // <a href="/link" data-ga="pageview:/vpv/custom/virtual/page">Link</a>

  // Be aware that the default page views are still sent with custom pageviews.

  // Note: This script is not loaded in IE6

  var HIT_TIMEOUT = 400;

  moj.Modules.GA = {
    init: function() {
      this.bindEvents();
    },

    bindEvents: function () {
      var that = this;

      $('a[data-ga]').on('click', function(evt) {
        var gaData = $(this).data('ga');
        var gaTypeValuePair = gaData.split(':');

        var type = gaTypeValuePair[0];
        var value = gaTypeValuePair[1];

        if(window.ga && _.includes(['event', 'pageview'], type) && value) {
          if(evt.preventDefault) {
            evt.preventDefault();
          } else {
            evt.returnValue = false;
          }

          that.send(type, gaTypeValuePair[1], $.proxy(function() {
            window.location.href = this.href;
          }, this));
        }
      });
    },

    _prepareEvent: function(payload, value) {
      var gaEvent = value.split('/');

      payload.eventCategory = gaEvent[0];
      payload.eventAction = gaEvent[1];

      if(gaEvent[2]) {
        payload.eventLabel = gaEvent[2];
      }

      if(gaEvent[3]) {
        payload.eventValue = gaEvent[3];
      }

      return payload;
    },

    send: function(type, value, cb) {
      var hitTimeout = setTimeout(cb, HIT_TIMEOUT);

      function exit() {
        clearTimeout(hitTimeout);

        if(cb) {
          cb();
        }
      }

      var payload = {
        hitType: type
      };

      if(type === 'event') {
        payload = this._prepareEvent(payload, value);

        // Exit if category or action are not defined
        if(!payload.eventCategory && !payload.eventAction) {
          exit();
        }
      }

      if(type === 'pageview') {
        payload.page = value;
      }

      payload.hitCallback = exit;

      // Only send GA event or pageview when required fields are specified
      if(payload.page || (payload.eventCategory && payload.eventAction)) {
        window.ga('send', payload);
      }
    }
  };
}());
