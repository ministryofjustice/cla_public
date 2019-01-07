  'use strict';
  var _ = require('lodash');
  moj.Modules.TruncateList = {
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
        var $listItems = $(this).find('> ul > li');

        if(!$listItems.length) {
          return;
        }

        this.remainingCount = $listItems.length - this.truncateItemCount;
        $listItems.slice(this.truncateItemCount).addClass('s-hidden');

        $listItems.slice(this.truncateItemCount).addClass('s-hidden');

        self.addExpandLink(this, $listItems);
      });
    },

    addExpandLink: function(listContainer, $listItems) {
      var expandButton = $(this.$expandButtonTemplate.replace('{count}', listContainer.remainingCount));
      var $listContainer = $(listContainer);

      expandButton.appendTo($listContainer);

      expandButton.on('click', function() {
        $listItems.removeClass('s-hidden').addClass('s-expanded');
        expandButton.remove();

        window.ga('send', 'event', 'org-list', 'expand', $listContainer.data('name'));
      });
    },

    templates: function () {
      var template = _.template($('#truncateListExpandLink').html());
      if(template) {
        this.$expandButtonTemplate = template();
      }
    }
  };

