(function(){
  'use strict';
  moj.Modules.Development = {
    el: '.context-debugger',

    init: function() {
      this.cacheEls();
      this.bindEvents();
    },

    cacheEls: function() {
      this.$contextDebugger = $(this.el);
    },

    bindEvents: function() {
      var self = this;

      this.$contextDebugger
        .on('click', '> button', $.proxy(this.handleToggle, this))
        .on('click', '._options a', function(evt) {
          evt.preventDefault();
          self.handleRequest(this.href, $.proxy(self.init, self));
        });
    },

    handleToggle: function() {
      this.$contextDebugger.toggleClass('s-expanded');
    },

    handleRequest: function(url, cb) {
      $.get(url, function(data) {
        var $data = $(data).find('#content');
        $data.find('.context-debugger').toggleClass('s-expanded');
        $('#content').replaceWith($data);

        cb();
      });
    }
  };
}());
