 'use strict';

moj.Modules.modalDialog = {
  init: function() {
    var GOVUK = global.GOVUK || {};
    GOVUK.modalDialog.containerSelector = '.main-content';
    GOVUK.modalDialog.warningMessage = 'Your session will end in';
    GOVUK.modalDialog.keepYouSecureMessage = 'For security reasons, any information you have entered will not be saved.'
    window.GOVUK.modalDialog.init();
  }
};

