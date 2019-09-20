 'use strict';
  require('./cookie-functions.js');
  require('govuk_publishing_components/components/cookie-banner.js');

  window.GOVUK.DEFAULT_COOKIE_CONSENT = {
    'essential': true,
    'usage': false,
    'brexit': false
  }

  window.GOVUK.setDefaultConsentCookie = function () {
    var defaultConsent = {
      'essential': true,
      'usage': false,
      'brexit': false
    }
    window.GOVUK.setCookie('cookie_policy', JSON.stringify(defaultConsent), { days: 365 })
  }

  window.GOVUK.approveAllCookieTypes = function () {
    var approvedConsent = {
      'essential': true,
      'usage': true,
      'brexit': true
    }

    window.GOVUK.setCookie('cookie_policy', JSON.stringify(approvedConsent), { days: 365 })
  }

  window.GOVUK.Modules.CookieBanner.prototype.isInCookiesPage = function () {
    return window.location.pathname === '/cookie-settings'
  }
