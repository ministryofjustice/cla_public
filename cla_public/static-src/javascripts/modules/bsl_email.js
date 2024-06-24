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
        moj.Modules.BSLEmail.handleToggle($('#adaptations-bsl_webcam')[0]);
      });

    },

    handleToggle: function(target) {
      var bsl_email_wrapper = $('#field-adaptations-bsl_email-wrapper');
      var email_wrapper = $("#field-email")
      var email = $('#email').val();
      if (target.checked && email === '') {
        bsl_email_wrapper.removeClass('s-hidden');
        email_wrapper.addClass('s-hidden');
      } else {
        bsl_email_wrapper.addClass('s-hidden');
        email_wrapper.removeClass('s-hidden');
      }
    }
  };

