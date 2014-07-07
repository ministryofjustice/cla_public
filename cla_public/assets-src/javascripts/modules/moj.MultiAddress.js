(function () {
  'use strict';

  moj.Modules.MultiAddress = {
    el: '.js-MultiAddress',

    init: function () {
      _.bindAll(this, 'render', 'addProperty', 'removeProperty');
      this.cacheEls();
      this.bindEvents();
    },

    cacheEls: function () {
      this.$addresses = $(this.el);
      this.count = 1;
    },

    bindEvents: function () {
      this.$addresses
        .on('click', '[value="add-property"]', this.addProperty)
        .on('click', '[value="remove-property"]', this.removeProperty);

      moj.Events.on('render', this.render);
    },

    render: function () {
      this.$addresses.append(CLA.templates.MultiAddress.addProperty());
      this.$addresses.find('.js-MultiAddress-property').each(function(i, el) {
        if (i > 0) {
          $(el).find('.js-MultiAddress-header').append(CLA.templates.MultiAddress.removeProperty());
        }
      });
    },

    addProperty: function () {
      this.$addresses.find('.u-jsHidden').first().removeClass('u-jsHidden');
      this.count = this.count + 1;

      if (this.count > 2) {
        this.$addresses.find('.js-MultiAddress-add').remove();
      }
    },

    removeProperty: function (e) {
      $(e.target).parents('.js-MultiAddress-property')
        .addClass('u-jsHidden')
        .find('[type=radio], [type=checkbox]').prop('checked', false)
        .end()
        .find('[type="number"]').val('');

      this.count = this.count - 1;

      if (this.count < 3 && this.$addresses.find('.js-MultiAddress-add').length < 1) {
        this.$addresses.append(CLA.templates.MultiAddress.addProperty());
      }
    }
  };
}());