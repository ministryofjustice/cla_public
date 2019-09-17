 'use strict';
  require('govuk_publishing_components/lib/cookie-functions.js');
  require('govuk_publishing_components/components/cookie-banner.js');


  window.GOVUK.setDefaultConsentCookie = function () {
    var defaultConsent = {
      'essential': true,
      'settings': true,
      'usage': false,
      'campaigns': false
    }
    window.GOVUK.setCookie('cookie_policy', JSON.stringify(defaultConsent), { days: 365 })
  }



