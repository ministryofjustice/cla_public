(function () {
  'use strict';
  moj.Templates = moj.Templates || {};
  moj.Templates.AddressFinder = moj.Templates.AddressFinder || {};

  moj.Templates.AddressFinder.addressList = _.template(
    '<dd class="form-row address-list">' +
      '<select name="address" class="form-control">' +
        '<option value="" disabled><%= count %> addresses found</option>' +
        '<option value="">-- Choose address --</option>' +
        '<% _.each(items, function(address, index) { %>' +
          '<option value="<%= index %>"><%= address %></option>' +
        '<% }); %>' +
      '</select>' +
    '</dd>'
  );

  moj.Templates.AddressFinder.findButton = _.template(
    '<button class="button-secondary address-finder-button" type="button">' +
      'Find UK address' +
    '</button>'
  );
}());
