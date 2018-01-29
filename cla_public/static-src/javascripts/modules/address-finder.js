'use strict';

var _ = require('lodash');

moj.Modules.AddressFinder = {
  el: '.address-finder',
  url: '/addresses/',

  init: function () {
    _.bindAll(this, 'render', 'onEnter', 'onclickFindBtn', 'onchangeAddress', 'queryAddressFinder', 'queryFail', 'querySuccess');
    this.cacheEls();
    this.bindEvents();
    this.templates();
  },

  cacheEls: function () {
    this.addresses = [];
    this.$postcode = $(this.el).find('input[type="text"]');
    this.$addressField = $(this.$postcode.data('address-el'));
    this.$postcodeRow = this.$postcode.closest('.form-row');
    this.$formGroup = this.$postcode.closest('.form-group-plain');
    this.$form = this.$postcode.parents('form');
  },

  bindEvents: function () {
    this.$postcode.on('keydown keypress', this.onEnter);
    this.$form.on('click', '.address-finder > button', this.onclickFindBtn);
    this.$form.on('change', '.address-list select', this.onchangeAddress);

    moj.Events.on('render AddressFinder.render', this.render);
  },

  onEnter: function (event) {
    if (event.which === 13) {
      event.preventDefault();
      this.$postcode.siblings('button').click();
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
      this.showError(this.postcodeNotEnteredTemplate());
    }
  },

  onchangeAddress: function (event) {
    this.updateAddress($(event.target).val());
    // remove address list
    $('.address-list').remove();
  },

  queryAddressFinder: function (postcode) {
    $.getJSON(this.url + postcode)
      .done(this.querySuccess)
      .fail(this.queryFail);
  },

  querySuccess: function (data) {
    this.$form.find('.address-finder-button').attr('disabled', false);

    // store addresses in module
    this.addresses = data;

    if (data.length < 1) {
      this.showError(this.noAddressesFoundTemplate());
    } else if (data.length === 1) {
      this.updatePostcode(data);
      this.updateAddress(0);
    } else {
      this.updatePostcode(data);
      this.renderAddressList(data);
    }
  },

  queryFail: function (jqxhr, textStatus, error) {
    this.$form.find('.address-finder-button').attr('disabled', false);

    this.showError(this.requestFailedTemplate({textStatus: textStatus, error: error}));
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

  render: function () {
    this.$postcode.after(' ' + $.trim(this.buttonTemplate()));
  },

  renderAddressList: function (addresses) {
    var $list = $('.address-list');
    var addrItems = [];

    // tidy up addresses for dropdown list
    $.each(addresses, function (i, addr) {
      var parts = addr.formatted_address.split('\n');
      var text = parts.join(', ');
      addrItems.push(text);
    });

    if ($list.length > 0) {
      $list.replaceWith(this.listTemplate({items: addrItems, count: addresses.length}));
    } else {
      this.$postcodeRow.after(this.listTemplate({items: addrItems, count: addresses.length}));
    }
    $('.address-list .form-control').focus();
  },

  showError: function (template) {
    this.$formGroup
      .addClass('m-error');
    this.$formGroup.find('.form-row')
      .before(template);
  },

  reset: function () {
    this.$formGroup
      .removeClass('m-error')
      .find('.field-error').remove();

    $('.address-list').remove();
  },

  templates: function () {
    this.listTemplate = _.template($('#addressFinderList').html());
    this.buttonTemplate = _.template($('#addressFinderButton').html());
    this.postcodeNotEnteredTemplate = _.template($('#postcodeNotEnteredText').html());
    this.noAddressesFoundTemplate = _.template($('#noAddressesFoundText').html());
    this.requestFailedTemplate = _.template($('#requestFailedText').html());
  }
};
