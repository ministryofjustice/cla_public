 'use strict';
  require('./cookie-functions.js');
  require('govuk_publishing_components/components/cookie-banner.js');

  window.GOVUK = window.GOVUK || {}
  var Modules = window.GOVUK.Modules || {};

  window.GOVUK.DEFAULT_COOKIE_CONSENT = {
    'essential': true,
    'usage': false,
    'gds': false
  }

  window.GOVUK.setDefaultConsentCookie = function () {
    var defaultConsent = {
      'essential': true,
      'usage': false,
      'gds': false
    }
    window.GOVUK.setCookie('cookie_policy', JSON.stringify(defaultConsent), { days: 365 })
  }

  window.GOVUK.approveAllCookieTypes = function () {
    var approvedConsent = {
      'essential': true,
      'usage': true,
      'gds': true
    }

    window.GOVUK.setCookie('cookie_policy', JSON.stringify(approvedConsent), { days: 365 })
    var event = new Event("cookies_approved");
    window.dispatchEvent(event, {"cookies": approvedConsent});
    moj.Modules.GA.send("pageview", document.location.pathname);
  }

  /*
  * Brexit cookie policy was renamed to gds.
  * Update existing cookie policies that contain a brexit value
  */
  var callback = Modules.CookieBanner.prototype.setupCookieMessage;
  Modules.CookieBanner.prototype.setupCookieMessage = function() {
    var cookie_policy = window.GOVUK.getConsentCookie();
    if (cookie_policy && typeof cookie_policy["brexit"] !== "undefined") {
      cookie_policy["gds"] = cookie_policy["brexit"];
      // Remove the previous cookie
      delete cookie_policy["brexit"];
      window.GOVUK.cookie("cookie_policy", null);
      // Set the new cookie that doesn't contain the brexit entry
      window.GOVUK.setConsentCookie(cookie_policy);
    }
    callback.call(this);
  }


