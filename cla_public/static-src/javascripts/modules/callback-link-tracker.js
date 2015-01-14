(function () {
  'use strict';

  moj.Modules.CallbackLinkTracker = {
    init: function() {
      $('#callback-link').on('click', function(evt) {
        evt.preventDefault();
        if(window.ga) {
          window.ga('send', 'event', 'callback', 'requested', window.location.pathname);
        }
        window.location.href = this.href;
      });
    }
  };
}());
