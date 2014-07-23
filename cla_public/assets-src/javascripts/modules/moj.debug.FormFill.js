/* jshint maxcomplexity:10 */
// Development module that is only loaded on dev and staging
// Dependencies: moj, _, jQuery

(function () {
  'use strict';

  moj.Modules.Development = {
    el: 'body',
    template: CLA.templates.Development.fillLinks,

    init: function () {
      _.bindAll(this, 'render', 'fillForm');
      this.cacheEls();
      this.bindEvents();
    },

    cacheEls: function () {
      this.$el = $(this.el);
      this.$form = ('#content form', this.$el);
      this.step = $('#id_checker_wizard-current_step').val();
    },

    bindEvents: function () {
      moj.Events.on('render', this.render);
      this.$el.on('click', '.js-FillForm', this.fillForm);
    },

    render: function () {
      $('.indicator').after(this.template({step: this.step}));
    },

    fillForm: function (e) {
      e.preventDefault();

      var $el = $(e.target),
          eligible = $el.data('eligible');

      switch(this.step) {
        case 'your_problem':
          this.fillProblem(eligible);
          break;
        case 'your_details':
          this.fillDetails(eligible);
          break;
        case 'your_benefits':
          this.fillBenefits(eligible);
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
        default:
          this.fillBasic();
      }

      this.$form.find('[type=submit]').focus();
    },

    fillBasic: function () {
      var $fields = $('form').find('input:not([type=submit], [type=hidden]), textarea, select');

      $fields.each(this.completeField);
    },

    completeField: function (i, el) {
      var $this = $(el),
          $label = $('label[for=' + $this.attr('id') + ']'),
          type = $this.prop('type'),
          val;

      if (type === 'text' || type === 'textarea') {
        val = $.trim($label.text().replace(/cannot be blank/g,''));
        $this.val(val);
      } else if (type === 'select-one') {
        $this.find('option:first').prop('selected', true);
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

    fillBenefits: function () {
      $('input[name=your_benefits-income_support]').prop('checked', true);
    },

    fillCapital: function () {
      $('input[type=number]:visible').val(0);
      $('input[value=1][name=property-0-main]').click();
      $('input[value=0][name=property-0-disputed]').click();
    },

    fillIncome: function (eligible) {
      $('input[type=number]').val(0);
      $('input[value=1][type=radio]').click();

      if (eligible) {
        $('#id_your_income-earnings_0').val(732.99+(285.13*3));
        $('#id_dependants-dependants_old').val(2);
        $('#id_dependants-dependants_young').val(1);
      } else {
        $('#id_your_income-earnings_0').val(910.51);
      }
    },

    fillAllowances: function () {
      $('input[type=number]').val(0);
    }
  };

})();