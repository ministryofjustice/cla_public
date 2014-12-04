(function () {
  'use strict';

  moj.Modules.LabelSelect = {
    el: '.block-label, .radio-inline',

    init: function() {
      _.bindAll(this, 'render');
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function() {
      this.$options
        .on('change', function () {
          var $el = $(this),
              $parent = $el.parent('label');

          // clear out all other selections on radio elements
          if ($el.attr('type') === 'radio') {
            $('[name=' + $el.attr('name') + ']').parent('label').removeClass('s-selected');
          }

          // set s-selected state on check
          if($el.is(':checked')){
            $parent.addClass('s-selected');
          } else {
            $parent.removeClass('s-selected');
          }
        });

      moj.Events.on('render LabelSelect.render', this.render);
    },

    cacheEls: function() {
      this.$options = $(this.el).find('input[type=radio], input[type=checkbox]');
    },

    render: function() {
      // keep current state
      this.$options.each(function () {
        var $el = $(this);
        if($el.is(':checked')){
          $el.parent().addClass('s-selected');
        }
      });
    }
  };
}());
