(function () {
  'use strict';

  moj.Modules.LabelSelect = {
    el: 'form',

    init: function () {
      this.cacheEls();
      this.bindEvents();

      // keep current state
      this.$options.each(function () {
        var $el = $(this);
        if($el.is(':checked')){
          $el.parent().addClass('is-selected');
        }
      });
    },

    bindEvents: function () {
      this.$options
        .on('change', function () {
          var $el = $(this),
              $parent = $el.parent('label');

          // clear out all other selections on radio elements
          if ($el.attr('type') === 'radio') {
            $('[name=' + $el.attr('name') + ']').parent('label').removeClass('is-selected');
          }

          // set is-selected state on check
          if($el.is(':checked')){
            $parent.addClass('is-selected');
          } else {
            $parent.removeClass('is-selected');
          }
        });
    },

    cacheEls: function () {
      this.$options = $(this.el).find('input[type=radio], input[type=checkbox]');
    }
  };
}());