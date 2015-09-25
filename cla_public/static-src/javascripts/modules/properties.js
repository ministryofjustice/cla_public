(function () {
  'use strict';

  moj.Modules.Properties = {
    init: function() {
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function() {
      var self = this;

      $('#PropertiesForm').on('submit', function(e) {
        var activeEl = document.activeElement;

        if(activeEl.type === 'submit' && activeEl.value) {
          e.preventDefault();
          self.handleAddRemoveButton(activeEl);
        } else {
          $.post('', self._injectFormData({}));
        }
      });
    },

    _injectFormData: function(data) {
      return this.$form.serializeArray().concat(data);
    },

    _updateForm: function(res) {
      this.$form.replaceWith($(res).find('#PropertiesForm'));

      this.init();
    },

    handleAddRemoveButton: function(button) {
      $.post('', this._injectFormData({
        name: button.name,
        value: button.value
      })).success($.proxy(this._updateForm, this));
    },

    cacheEls: function() {
      this.$form = $('#PropertiesForm');
    }
  };
}());
