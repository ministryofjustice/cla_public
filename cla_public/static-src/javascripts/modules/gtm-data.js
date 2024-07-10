'use strict';

moj.Modules.GMTData = {

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

      value = value.trim().replace(/\n/g,'').substr(0,30); // can be up to 100 if needed

      GTM.push({ 
        'event': 'element-' + e.type, 
        'element_tag': elem, 
        'element_id': $(this).attr('id'), 
        'element_value': value,
        'element_checked': $(this).is(':checked')     
      });
    });
  }
}
