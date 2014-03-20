(function () {
  'use strict';

  moj.Modules.LabelFocus = {
    el: 'form',

    init: function () {
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function () {
      // set focused selector to parent label
      this.$options
        .on('focus', function () {
          $(this).parent('label').addClass('is-focused');
        })
        .on('focusout', function () {
          $('.is-focused').removeClass('is-focused');
        });
    },

    cacheEls: function () {
      this.$options = $(this.el).find('input[type=radio], input[type=checkbox]');
    }
  };
}());
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
/* globals _ */

(function () {
  'use strict';

  moj.Modules.Conditional = {
    el: '.js-Conditional',

    init: function () {
      _.bindAll(this, 'render');
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function () {
      this.$conditionals.on('change deselect', this.toggle);
      moj.Events.on('render', this.render);
    },

    cacheEls: function () {
      this.$conditionals = $(this.el);
    },

    render: function () {
      this.$conditionals.each(this.toggle);
    },

    toggle: function (e) {
      var $el = $(this),
          $conditionalEl = $('#' + $el.data('conditionalEl'));

      // trigger a deselect event if a change event occured
      if (e.type === 'change') {
        $('input[name="' + $el.attr('name') + '"]').not($el).trigger('deselect');
      }

      // if a conditional element has been set, run the checks
      if ($el.data('conditionalEl')) {
        $el.attr('aria-control', $el.data('conditionalEl'));

        // if checked show/hide the extra content
        if($el.is(':checked')){
          $conditionalEl.show();
          $conditionalEl.attr('aria-expanded', 'true').attr('aria-hidden', 'false');
        } else {
          $conditionalEl.hide();
          $conditionalEl.attr('aria-expanded', 'false').attr('aria-hidden', 'true');
        }
      }
    }
  };
}());
(function () {
  'use strict';

  moj.Modules.Shame = {
    init: function () {
      // Polyfill a given set of elements
      $('details').details();
      $('body').addClass($.fn.details.support ? 'details' : 'no-details');
    }
  };
}());