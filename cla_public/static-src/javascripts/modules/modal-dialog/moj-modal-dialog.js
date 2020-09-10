 'use strict';

moj.Modules.modalDialog = {
  init: function() {
    var GOVUK = global.GOVUK || {};
    GOVUK.modalDialog.containerSelector = '.main-content';
    if (GOVUK.getCookie("locale") == "cy_GB") {
      GOVUK.modalDialog.warningMessage = 'Bydd eich sesiwn yn dod i ben mewn';
      GOVUK.modalDialog.keepYouSecureMessage = 'Am resymau diogelwch, ni fydd unrhyw wybodaeth rydych wedi’i mewnbynnu yn cael ei chadw.';
    } else {
      GOVUK.modalDialog.warningMessage = 'Your session will end in';
      GOVUK.modalDialog.keepYouSecureMessage = 'For security reasons, any information you have entered will not be saved.';
    }
    window.GOVUK.modalDialog.init();
  }
};

