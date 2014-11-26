(function () {
  'use strict';

  moj.Modules.AddressFinder = {
    el: '.js-AddressFinder',
    url: '/addressfinder/addresses/',

    init: function () {
      _.bindAll(this, 'render', 'onEnter', 'onclickFindBtn', 'onchangeAddress', 'queryAddressFinder', 'queryFail', 'querySuccess');
      this.cacheEls();
      this.bindEvents();
    },

    cacheEls: function () {
      this.addresses = [];
      this.$postcode = $(this.el);
      this.$addressField = $(this.$postcode.data('address-el'));
      this.$postcodeRow = this.$postcode.parents('.FormRow');
      this.$postcodeLabel = this.$postcodeRow.find('.FormRow-label');
      this.$form = this.$postcode.parents('form');
    },

    bindEvents: function () {
      this.$postcode.on('keydown keypress', this.onEnter);
      this.$form.on('click', '.js-AddressFinder-button', this.onclickFindBtn);
      this.$form.on('change', '.js-AddressFinder-options', this.onchangeAddress);

      moj.Events.on('render AddressFinder.render', this.render);
    },

    onEnter: function (event) {
      if (event.which === 13) {
        event.preventDefault();
        this.$form.find('.js-AddressFinder-button').click();
      }
    },

    onclickFindBtn: function (event) {
      var $el = $(event.target);
      var query = this.$postcode.val();

      // clear errors
      this.reset();

      if (query) {
        $el.attr('disabled', true);
        this.queryAddressFinder(query);
      } else {
        this.showError('must contain a valid postcode');
      }
    },

    onchangeAddress: function (event) {
      this.updateAddress($(event.target).val());
      // remove address list
      $('.js-AddressFinder-addressList').remove();
    },

    queryAddressFinder: function (postcode) {
      $.getJSON(this.url, {
        'postcode': postcode,
        'fields': 'formatted_address'
      })
        .done(this.querySuccess)
        .fail(this.queryFail);
    },

    querySuccess: function (data) {
      this.$form.find('.js-AddressFinder-button').attr('disabled', false);

      // store addresses in module
      this.addresses = data;

      if (data.length < 1) {
        this.showError('No addresses were found with that postcode');
      } else if (data.length === 1) {
        this.updatePostcode(data);
        this.updateAddress(0);
      } else {
        this.updatePostcode(data);
        this.renderAddressList(data);
      }
    },

    queryFail: function (jqxhr, textStatus, error) {
      this.$form.find('.js-AddressFinder-button').attr('disabled', false);

      this.showError('Request failed: ' + textStatus + ', ' + error);
    },

    updatePostcode: function (data) {
      var addr = data[0].formatted_address;
      var postcode = addr.split('\n').pop();
      this.$postcode.val(postcode);
    },

    updateAddress: function (index) {
      var addr = this.addresses[index];
      var parts = addr.formatted_address.split('\n');
      parts.pop();  // strip postcode
      this.$addressField.val(parts.join('\n')).focus();
    },

    render: function (addr) {
      this.$postcode.after(CLA.templates.AddressFinder.findButton());
    },

    renderAddressList: function (addresses) {
      var $list = $('.js-AddressFinder-addressList');
      var addrItems = [];

      // tidy up addresses for dropdown list
      $.each(addresses, function (i, addr) {
        var parts = addr.formatted_address.split('\n');
        var postcode = parts.pop();
        var text = parts.join(', ');
        addrItems.push(text);
      });

      if ($list.length > 0) {
        $list.replaceWith(CLA.templates.AddressFinder.addressList({items: addrItems, count: addresses.length}));
      } else {
        this.$postcodeRow.after(CLA.templates.AddressFinder.addressList({items: addrItems, count: addresses.length}));
      }
      $('.js-AddressFinder-options').focus();
    },

    showError: function (msg) {
      this.$postcodeRow.addClass('Error');
      this.$postcodeLabel.append($('<span class="Error-message">' + msg + '</span>'));
    },

    reset: function () {
      this.$postcodeRow
        .removeClass('Error')
        .find('.Error-message').remove();

      $('.js-AddressFinder-addressList').remove();
    }
  };
}());
