 'use strict';
  /**
   * This was part of the jinja-moj-template python package (moj_template/static/javascripts/govuk-template.js)
   * We are deprecating the use of this package and moving to govuk_front
   * As part of that deprecation we are taking the relevant parts and adding them as js modules
   */

  moj.Modules.headerNavigation = {
    init: function () {
      this.addFixes();
    },

    addFixes: function () {
      // fix for printing bug in Windows Safari
      var windowsSafari = (window.navigator.userAgent.match(/(\(Windows[\s\w\.]+\))[\/\(\s\w\.\,\)]+(Version\/[\d\.]+)\s(Safari\/[\d\.]+)/) !== null),
          style;

      if (windowsSafari) {
        // set the New Transport font to Arial for printing
        style = document.createElement('style');
        style.setAttribute('type', 'text/css');
        style.setAttribute('media', 'print');
        style.innerHTML = '@font-face { font-family: nta !important; src: local("Arial") !important; }';
        document.getElementsByTagName('head')[0].appendChild(style);
      }
    }
  };
