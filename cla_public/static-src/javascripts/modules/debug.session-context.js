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

          var formAction = $(this).data('form-action');

          self.handleRequest(this.href, function() {
            $.proxy(self.init, self);

            if(formAction) {
              $('form').trigger(formAction);
            }
          });
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

        moj.Modules.ConditionalSubfields.init();

        cb();
      });
    }
  };
}());
