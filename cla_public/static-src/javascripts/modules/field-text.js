(function () {
  'use strict';

  moj.Modules.FieldHelp = {
    moreInfos: [],

    init: function() {
      this.cacheEls();
      this.bindEvents();
      this.addMoreInfoLink();
    },

    bindEvents: function() {
      this.moreInfos.parent()
        .on('click', 'a', this.handleToggle);
    },

    handleToggle: function(evt) {
      $(evt.target).parent().toggleClass('s-expanded');
    },

    addMoreInfoLink: function() {
      $.each(this.moreInfos, function(i, el) {
        $('<a class="field-more-info-toggle">more info</a>').insertBefore($(el));
      });
    },

    cacheEls: function() {
      this.moreInfos = $('.field-more-info');
    }
  };
}());
