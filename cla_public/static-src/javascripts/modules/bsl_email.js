 'use strict';

  moj.Modules.BSLEmail = {
    moreInfos: [],

    init: function() {
      this.bindEvents();
    },

    bindEvents: function() {
      $('#adaptations-bsl_webcam').on('click', function (){
        moj.Modules.BSLEmail.handleToggle(this);
      });

      $('#field-adaptations-bsl_email').on('error', function (errors){
        $('#field-bsl-email-wrapper').removeClass("govuk-inset-text");
        moj.Modules.BSLEmail.handleToggle($('#adaptations-bsl_webcam')[0]);
      });

    },

    handleToggle: function(target) {
      var field_bsl_email_wrapper = $('#field-bsl-email-wrapper');
      var field_email = $("#field-email")
      var email = $('#email').val();
      if (target.checked && email === '') {
        field_bsl_email_wrapper.removeClass('s-hidden');
        field_email.addClass('s-hidden');
      } else {
        field_bsl_email_wrapper.addClass('s-hidden');
        field_email.removeClass('s-hidden');
      }
    }
  };

