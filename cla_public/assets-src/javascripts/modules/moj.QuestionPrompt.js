/* globals _ */

(function () {
  'use strict';

  moj.Modules.FormHelper = {
    el: '.js-QuestionPrompt',

    init: function () {
      _.bindAll(this, 'render', 'inputChange', 'changeAnswer');
      this.cacheEls();
      this.bindEvents();
    },

    bindEvents: function () {
      this.$questions
        .on('change', 'input[type=radio], input[type=checkbox]', this.inputChange)
        .on('click', '.QuestionPrompt-change', this.changeAnswer);
      moj.Events.on('render', this.render);
    },

    cacheEls: function () {
      this.$questions = $(this.el);
    },

    render: function () {
      this.$questions.filter(':not(:first)').find('label').hide();
      this.$questions.filter(':first').addClass('QuestionPrompt--active');
    },

    inputChange: function (e) {
      var $this = $(e.target),
          $fieldset = $this.closest(this.el),
          answer = $this.val() === 1 ? 'Yes' : 'No';

      // remove previous current classes
      $('.QuestionPrompt--active').removeClass('QuestionPrompt--active');

      $fieldset
        .append('<p class="QuestionPrompt-answer">You answered: ' + answer + ' <br><a href="#" class="QuestionPrompt-change">Change answer</a></p>')
        .find('label').hide()
        .end()
        .next().addClass('QuestionPrompt--active').find('.QuestionPrompt-answer').hide()
        .end()
        .find('label').show();

      if ($fieldset.find('summary').attr('aria-expanded') === 'true') {
        $fieldset.find('summary').click();
      }
    },

    changeAnswer: function (e) {
      e.preventDefault();

      var $fieldset = $(e.target).closest(this.el);

      // remove previous current classes
      $('.QuestionPrompt--active').removeClass('QuestionPrompt--active');

      this.$questions.find('label').hide();
      $fieldset
        .addClass('QuestionPrompt--active')
        .find('label').show()
        .end()
        .find('.QuestionPrompt-answer').hide();
    }
  };
}());