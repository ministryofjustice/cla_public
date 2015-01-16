(function () {
  'use strict';

  moj.Modules.PrintPageButton = {
    init: function() {
      this.initTemplates();
      this.renderButton();
    },

    renderButton: function() {
      var contentArea = $('.confirmation');

      if(!contentArea.length || !this.printButton || !this.printButton.length) {
        return;
      }

      contentArea.append(this.printButton);

      this.printButton.on('click', function() {
        window.print();
      });
    },

    initTemplates: function() {
      var template = $('#printButtonTemplate');

      if(template.length) {
        this.printButton = $(_.template(template.html())());
      }
    }
  };
}());
