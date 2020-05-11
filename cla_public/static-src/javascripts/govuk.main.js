  'use strict';
  require('govuk_publishing_components/modules.js');
  var govukFrontend = require('govuk-frontend');
  window.GOVUKFrontend = govukFrontend;

  $(document).ready(function () {
    window.GOVUK.modules.start();
  });
