'use strict';

//Google Tag Manager

var GTM_Loaded = false;

function add_GTM() {
  
  // Standard GTM code
  (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});

  // Insert our variable into data layer
  if(typeof GTM_ANON_ID !== 'undefined' && GTM_ANON_ID.length === 36) {
	  window.dataLayer = window.dataLayer || [];
	  window.dataLayer.push({ user_id: GTM_ANON_ID });
	}

	// Continue standard GTM code
  var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-M9QXCZWK');

  GTM_Loaded = true;
}

// If user consents from banner then allow GTM to load
window.addEventListener("cookies_approved", function(event){
  if(!GTM_Loaded)add_GTM();
})

// If user had consented already then allow GTM to load
if (document.cookie && document.cookie.indexOf('cookie_policy={"essential":true,"usage":true') > -1 && !GTM_Loaded) {
	add_GTM();
}	
