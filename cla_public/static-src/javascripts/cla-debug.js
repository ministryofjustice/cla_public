(function(){
  'use strict';

  function init() {
    var $contextDebugger = $('.context-debugger');

    $contextDebugger.find('> button').on('click', function(evt) {
      evt.preventDefault();
      window.debuggerExpanded = !window.debuggerExpanded;

      $contextDebugger.toggleClass('s-expanded', window.debuggerExpanded);
    });

    $contextDebugger.find('._options a').on('click', function(evt) {
      evt.preventDefault();

      $.get(this.href, function(data) {
        var $data = $(data).find('#content');
        $data.find('.context-debugger').toggleClass('s-expanded');
        $('#content').replaceWith($data);

        init();
      });
    });
  }

  init();
}());
