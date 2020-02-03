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

      moj.init();
    },

    handleAddRemoveButton: function(button) {
      var self = this;

      $.post('', this._injectFormData({
        name: button.name,
        value: button.value
      })).success(function(res) {
        self._updateForm(res);

        var totalProperties = self.$form.find('.fieldset-group').length;

        window.ga('send', 'event', 'property', button.name + ' / total:' + totalProperties);

        $("#PropertiesForm>.govuk-form-group").get(-1).scrollIntoView(); //scrolls to last property on screen

      });
    },

    cacheEls: function() {
      this.$form = $('#PropertiesForm');
    }
  };

