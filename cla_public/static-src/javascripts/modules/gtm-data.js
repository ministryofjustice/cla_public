'use strict';
moj.Modules.GTMData = {

  init: function() {

    if(!window.dataLayer)return;

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

      window.dataLayer.push({
        'event': 'element-' + e.type,
        'element_tag': elem,
        'element_id': $(this).attr('id'),
        'element_value': value,
        'element_checked': $(this).is(':checked')
      });
    });

    this.trackFALASearch();
    
    // Delay to allow browser to calculate timings
    setTimeout('moj.Modules.GTMData.trackPageLoadTime()',1000);
  },

  trackFALASearch: function() {
      
    if(window.location.pathname !== '/scope/refer/legal-adviser' ||
      typeof RESOLVED_POSTCODE !== 'string' ||
      typeof CATEGORY !=='string' ||
      typeof CLOSEST_PROVIDER_MILEAGE !=='string')return;

    var match = RESOLVED_POSTCODE.replace(/\s/g, '').match(/^(.+?)(\d[A-Z]{2})$/i);
    var district = match ? match[1] : '';

    var mileage = !isNaN(CLOSEST_PROVIDER_MILEAGE) ? parseFloat(CLOSEST_PROVIDER_MILEAGE).toFixed(2).toString() : '';

    window.dataLayer.push({
      'event': 'fala_search',
      'district': district,
      'category_name': CATEGORY.substring(0,50),
      'closest_provider_mileage': mileage
    });
  },

  trackPageLoadTime: function() {

    var labels = {
      excellent: 'Under 1 second (Excellent)',
      veryGood: '1 to 2 seconds (Very good)',
      acceptable: '2 to 3 seconds (Acceptable)',
      improve: '3 to 5 seconds (Try improving)',
      fix: 'More than 5 seconds (Needs fixing)'
    }

    var getLoadTimeSeconds = function() {
      if(typeof performance === 'undefined' || !performance || !performance.getEntriesByType 
        || !performance.getEntriesByType('navigation')[0]) return false;

      return performance.getEntriesByType('navigation')[0].duration / 1000;
    };

    var labelLoadTime = function(loadTime) {
      return  loadTime < 1 ? labels.excellent : 
              loadTime < 2 ? labels.veryGood : 
              loadTime < 3 ? labels.acceptable : 
              loadTime < 5 ? labels.improve : labels.fix;
    };
      
    var loadTime = getLoadTimeSeconds();
    if(!loadTime || isNaN(loadTime)) return;
              
    var label = labelLoadTime(loadTime);
    
    window.dataLayer.push({
      'event': 'page_load_time',
      'variable_label': label,
      'variable_number': parseFloat(loadTime).toFixed(2).toString()
    });
  }
}
