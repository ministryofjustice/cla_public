'use strict';
moj.Modules.GTMData = {
  init: function() {

    var GTM = window.dataLayer;
    if(!GTM)return;

    // Track element clicks and form element changes
    $('input, select, button, textarea').on('click change', function(e){

      var clickInputTypes = ['checkbox', 'radio', 'button', 'textarea'];
      var thisIsAClickInput = clickInputTypes.includes($(this).attr('type'));

      // Don't track changes for clickable input types, only clicks
      if(e.type === 'change' && thisIsAClickInput)return;

      var elem = $(this).prop('tagName').toLowerCase();
      var value = '';

      switch(elem) {
        case 'textarea':
        case 'input': value = thisIsAClickInput ? $(this).val() : 'Redacted'; break;
        case 'button': value = $(this).text(); break;
        case 'select': value = $(this).find('option:selected').text(); break;
      }

      value = value.trim().replace(/\n/g,'').substring(0,30); // can be up to 100 if needed

      GTM.push({
        'event': 'element-' + e.type,
        'element_tag': elem,
        'element_id': $(this).attr('id'),
        'element_value': value,
        'element_checked': $(this).is(':checked')
      });
    });

    // Track FALA-lite input
    this.trackFALA();
  },

  trackFALA: function() {
          
    if(window.location.pathname !== '/scope/refer/legal-adviser' ||
      typeof RESOLVED_POSTCODE !== 'string' || 
      typeof CATEGORY !=='string' || 
      typeof CLOSEST_PROVIDER_MILEAGE !=='string')return;

    var match = RESOLVED_POSTCODE.match(/^(.+?)(\d[A-Z]{2})$/i);
    var district = match ? match[1] : '';

    var mileage = !isNaN(CLOSEST_PROVIDER_MILEAGE) ? CLOSEST_PROVIDER_MILEAGE : '';

    var GTM = window.dataLayer;
    GTM.push({
      'event': 'fala_search',
      'district': district,
      'category': CATEGORY.substring(0,50),
      'closest_provider': mileage
    });

    console.log({
      'event': 'fala_search',
      'district': district,
      'category': CATEGORY.substring(0,50),
      'closest_provider': mileage
    });
  }
}