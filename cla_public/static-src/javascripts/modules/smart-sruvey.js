  'use strict';

  moj.Modules.SmartSurvey = {
    init: function() {
      console.log("Adding smart survey");
      var _ssq={'cid':1139766};
      var ss=document.createElement('script');
      ss.type='text/javascript';
      ss.async=true;
      ss.src=('https:'==document.location.protocol?'https://':'http://')+'www.smartsurvey.co.uk/s/popup/'+_ssq.cid+'/js/';var s=document.getElementsByTagName('script')[0];
      document.body.appendChild(ss);
    }
  };
