(function() {
  'use strict';

  moj.Modules.BoxToggle = {
    el: '[data-truncate]',

    init: function() {
      this.cacheEls();
      this.templates();
      this.processLists();
    },

    cacheEls: function() {
      this.$truncatedLists = $(this.el).filter(function() {
        var value = $(this).data('truncate');
        var isValidCount = _.isNumber(value) && value > 0;
        this.truncateItemCount = isValidCount ? value : 0;
        return isValidCount;
      });
    },

    processLists: function() {
      if(!this.$truncatedLists.length) {
        return;
      }

      var self = this;

      this.$truncatedLists.each(function() {
        var listItems = $(this).find('> ul > li');
        this.remainingCount = listItems.length - this.truncateItemCount;
        listItems.slice(this.truncateItemCount).addClass('s-hidden');

        self.addExpandLink(this, listItems);
      });
    },

    addExpandLink: function(list, listItems) {
      var expandButton = $(this.$expandButtonTemplate.replace('{count}', list.remainingCount));
      expandButton.appendTo($(list));

      expandButton.on('click', function() {
        listItems.removeClass('s-hidden').addClass('s-expanded');
        expandButton.remove();
      });
    },

    templates: function () {
      var template = _.template($('#truncateListExpandLink').html());
      if(template) {
        this.$expandButtonTemplate = template();
      }
    }
  };
}());
