(function () {
  'use strict';

  // test for html5 storage
  moj.Helpers.hasHtml5Storage = function() {
    try {
      return 'sessionStorage' in window && window.sessionStorage !== null;
    } catch (e) {
      return false;
    }
  };

  // helper to return the scroll position of an element
  moj.Helpers.scrollTo = function(e) {
    var $target = e.target !== undefined ? $($(e.target).attr('href')) : $(e),
        $scrollEl = $('html, body'),
        topPos = moj.Helpers.scrollPos($target);

    $scrollEl
      .animate({
        scrollTop: topPos
      }, 300)
      .promise()
      .done(function() {
        $target.closest('.FormRow, form').find('input:not([type=hidden]), select, textarea').first().focus();
      });
  };

  // helper to return the scroll position of an element
  moj.Helpers.scrollPos = function(target) {
    /*jshint laxbreak: true */
    return target.offset().top;
  };

  // Handlebars Helpers
  Handlebars.registerHelper('formatCurrency', function(value) {
    return parseFloat(value).toFixed(2);
  });
})();