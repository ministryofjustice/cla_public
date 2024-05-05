// Initialise Google Tag Manager. Not in MoJ Modules as it should run in head tag
// rather than bottom of the page.

var GTM_Loaded = false;

function add_GTM() {
  // Standard GTM code
  (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','GTM-M9QXCZWK');
  
  GTM_Loaded = true;
},

// If user consents to cookies using button, load GTM
window.addEventListener("cookies_approved", function(event){
  if(!GTM_Loaded)add_GTM();
});

// If user had consented already, load GTM
if (window.GOVUK.checkConsentCookieCategory('', 'usage')) {
  if(!GTM_Loaded)add_GTM();
}
