(function () {
  'use strict';

  moj.Modules.LabelSelect = {
    el: '.block-label, .radio-inline',

    init: function() {
      _.bindAll(this, 'render');
      this.cacheEls();
      this.bindEvents();
      this.processQueryString();
    },

    bindEvents: function() {
      this.$options
        .on('change label-select', function () {
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

    processQueryString: function() {
      var queryString = _.chain(location.search.slice(1).split('&'))
        .map(function(item) {
          if(item) {
            var pair = item.split('=');
            return pair[1] ? pair : '';
          }
        })
        .compact()
        .object()
        .value();

      // Select fields found in query string
      _.forOwn(queryString, function(value, key) {
        if(value) {
          $('[name="' + key + '"][value="' + value + '"]').click();
        }
      });
    },

    render: function() {
      this.$options.filter(':checked').each(function(){
        $(this).parent().addClass('s-selected');
      });
    }
  };
}());
