// Development module that is only loaded on dev and staging
// Dependencies: moj, _, jQuery

(function () {
  'use strict';

  moj.Modules.Development = {
    el: '#wrapper',
    template: CLA.templates.Development.fillLinks(),

    init: function () {
      _.bindAll(this, 'render', 'fillForm');
      this.cacheEls();
      this.bindEvents();
    },

    cacheEls: function () {
      this.$el = $(this.el);
    },

    bindEvents: function () {
      moj.Events.on('render', this.render);
      this.$el.on('click', '.js-FillForm', this.fillForm);
    },

    render: function () {
      if ($('.ProgressIndicator').attr('aria-valuetext') !== 'Step 4 of 4') {
        $('.ProgressIndicator').after(this.template);
      }
    },

    fillForm: function (e) {
      e.preventDefault();

      var $el = $(e.target),
          eligible = $el.data('eligible'),
          step = $('#id_checker_wizard-current_step').val();

      switch(step) {
        case 'your_problem':
          this.fillProblem(eligible);
          break;
        case 'your_details':
          this.fillDetails(eligible);
          break;
        case 'your_capital':
          this.fillCapital();
          break;
        case 'your_income':
          this.fillIncome(eligible);
          break;
        case 'your_allowances':
          this.fillAllowances();
          break;
      }
    },

    fillProblem: function (eligible) {
      if (eligible) {
        $('#id_your_problem-category_2').click();
      } else {
        $('#id_your_problem-category_0').click();
      }
    },

    fillDetails: function (eligible) {
      if (eligible) {
        $('input[value=1][type=radio]').click();
      } else {
        $('input[value=0][type=radio]').click();
      }
    },

    fillCapital: function () {
      $('input[type=number]').val(0);
      $('input[value=1][name=property-0-owner]').click();
      $('input[value=0][name=your_other_properties-other_properties]').click();
    },

    fillIncome: function (eligible) {
      $('input[type=number]').val(0);
      $('input[value=1][type=radio]').click();

      if (eligible) {
        $('#id_your_income-earnings').val(732.99+(285.13*3));
        $('#id_dependants-dependants_old').val(2);
        $('#id_dependants-dependants_young').val(1);
      } else {
        $('#id_your_income-earnings').val(910.51);
      }
    },

    fillAllowances: function () {
      $('input[type=number]').val(0);
    }
  };

})();