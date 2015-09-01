(function(){
  'use strict';
  moj.Modules.Development = {
    el: '.context-debugger',

    init: function() {
      this.bindEvents();
    },

    bindEvents: function() {
      var self = this;

      $('body')
        .on('click', function(e) {
          var $contextDebugger = $('.context-debugger');
          var $target = $(e.target);
          if($contextDebugger.hasClass('s-expanded') && !$target.closest('.context-debugger').length) {
            $contextDebugger.toggleClass('s-expanded');
          }
        })
        .on('click', '.context-debugger > button', function() {
          $(this).parent().toggleClass('s-expanded');
        })
        .on('click', '.context-debugger ._options a', function(e) {
          e.preventDefault();

          var $selectedOption = $(this);
          var existingSelectedOptions = [];
          var formAction = $(this).data('form-action');
          var url = this.href;

          if(!formAction) {
            $(this).closest('.context-debugger').find('._selected:not([data-form-action])').map(function() {
              if($(this).closest('li').text() === $selectedOption.closest('li').text()) {
                return;
              }
              existingSelectedOptions.push($(this).attr('href').replace(/^\?/, ''));
            });
            url = $selectedOption.attr('href') + '&' + existingSelectedOptions.join('&');
          }

          self.handleRequest(url, function () {
            $.proxy(self.init, self);

            if (formAction) {
              $('form').trigger(formAction);
            }
          });
        });
    },

    handleRequest: function(url, cb) {
      $.get(url, function(data) {
        var $formData = $(data).find('form');
        var $debuggerMenu = $(data).find('.context-debugger > menu');
        $('form').replaceWith($formData);
        $('.context-debugger > menu').replaceWith($debuggerMenu);

        moj.Modules.ConditionalSubfields.init();

        cb();
      });
    }
  };
}());
