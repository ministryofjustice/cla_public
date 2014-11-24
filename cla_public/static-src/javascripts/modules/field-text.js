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
      var $fieldHelp = $(evt.target).parent();
      $fieldHelp
        .toggleClass('s-expanded')
        .find('.field-more-info')
          .attr('aria-expanded', function() {
            return $(this).attr('aria-expanded') === 'false';
          });
    },

    addMoreInfoLink: function() {
      $.each(this.moreInfos, function(i, el) {
        $(this).attr('aria-expanded', 'false');
        $('<a class="field-more-info-toggle" role="button">more info</a>')
          .insertBefore($(el));
      });
    },

    cacheEls: function() {
      this.moreInfos = $('.field-more-info');
    }
  };
}());
