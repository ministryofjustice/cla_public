  'use strict';

  moj.Modules.SmartSurvey = {
    init: function() {
      if (window.SMART_SURVEY_CID == "") {
        return;
      }
      window._ssq={'cid':window.SMART_SURVEY_CID};
      var ss=document.createElement('script');
      ss.type='text/javascript';
      ss.async=true;
      ss.src=('https:'==document.location.protocol?'https://':'http://')+'www.smartsurvey.co.uk/s/popup/'+window._ssq.cid+'/js/';var s=document.getElementsByTagName('script')[0];
      document.body.appendChild(ss);
    }
  };
