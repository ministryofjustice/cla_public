 'use strict';
  /**
   * This was part of the jinja-moj-template python package (moj_template/static/javascripts/govuk-template.js)
   * We are deprecating the use of this package and moving to govuk_front
   * As part of that deprecation we are taking the relevant parts and adding them as js modules
   */

  moj.Modules.safariFixes = {
    init: function () {
      this.bindEvents();
    },

    bindEvents: function () {
      // header navigation toggle
      if (document.querySelectorAll && document.addEventListener){
        var els = document.querySelectorAll('.js-header-toggle'),
            i, _i;
        for(i=0,_i=els.length; i<_i; i++){
          els[i].addEventListener('click', function(e){
            e.preventDefault();
            var target = document.getElementById(this.getAttribute('href').substr(1)),
                targetClass = target.getAttribute('class') || '',
                sourceClass = this.getAttribute('class') || '';

            if(targetClass.indexOf('js-visible') !== -1){
              target.setAttribute('class', targetClass.replace(/(^|\s)js-visible(\s|$)/, ''));
            } else {
              target.setAttribute('class', targetClass + " js-visible");
            }
            if(sourceClass.indexOf('js-hidden') !== -1){
              this.setAttribute('class', sourceClass.replace(/(^|\s)js-hidden(\s|$)/, ''));
            } else {
              this.setAttribute('class', sourceClass + " js-hidden");
            }
          });
        }
      }
    }
  };
