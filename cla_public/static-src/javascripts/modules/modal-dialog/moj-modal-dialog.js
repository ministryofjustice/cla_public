 'use strict';

moj.Modules.modalDialog = {
  init: function() {
    var GOVUK = global.GOVUK || {};
    GOVUK.modalDialog.containerSelector = '.main-content';
    window.GOVUK.modalDialog.init();
  }
};

