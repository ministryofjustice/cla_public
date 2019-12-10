 'use strict';

moj.Modules.modalDialog = {
  init: function() {
    var GOVUK = global.GOVUK || {};
    GOVUK.modalDialog.containerSelector = '.main-content';
    GOVUK.modalDialog.warningMessage = {% trans %}'Your session will end in'{% endtrans %};
    GOVUK.modalDialog.keepYouSecureMessage = {% trans %}'For security reasons, any information you have entered will not be saved.'{% endtrans %};
    window.GOVUK.modalDialog.init();
  }
};

